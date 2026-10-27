"""Tests for view_generator module."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from structurizr_mkdocs_generatr.view_generator import (
    DslDeploymentEnvironment,
    DslDeploymentZone,
    DslGroup,
    DslSoftwareSystem,
    DslUser,
    _generate_container_views,
    _generate_deployment_views,
    _generate_landscape_views,
    _generate_system_context_views,
    _parse_deployments,
    _parse_groups,
    _parse_monolithic_dsl,
    _parse_users,
    _resolve_deployed_systems,
    generate_views,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_workspace(tmp_path: Path) -> Path:
    """Create a minimal workspace directory for testing."""
    ws = tmp_path / "workspace"
    ws.mkdir()

    users_dir = ws / "workspace-includes"
    users_dir.mkdir(parents=True)

    (users_dir / "users.dsl").write_text(
        'userAlice = person "Alice" "Developer" {\n}\n\n'
        'userBob = person "Bob" "Analyst" {\n}\n',
        encoding="utf-8",
    )

    groups_dir = users_dir / "groups"
    groups_dir.mkdir()
    (groups_dir / "engineering.dsl").write_text(
        'groupEngineering = group "Engineering" {\n'
        '    softwareSystemBackend = softwareSystem "Backend" "Core API" {\n'
        '        containerBackendApi = container "Backend API" "REST API" "Node.js" "SERVICE" {\n'
        '            userAlice -> this "Develops"\n'
        "        }\n"
        '        containerBackendDb = container "Backend Database" "Data store" "PostgreSQL" "DATASET" {\n'
        "        }\n"
        "    }\n"
        '    softwareSystemFrontend = softwareSystem "Frontend" "Web app" {\n'
        '        containerFrontendUi = container "Frontend UI" "SPA" "React" "UI_ELEMENT" {\n'
        '            userBob -> this "Uses reports"\n'
        "        }\n"
        "    }\n"
        "}\n",
        encoding="utf-8",
    )
    (groups_dir / "external.dsl").write_text(
        'groupExternal = group "External" {\n'
        '    softwareSystemEmail = softwareSystem "Email Service" "Sends emails" "External System" {\n'
        "    }\n"
        "}\n",
        encoding="utf-8",
    )

    deploy_dir = users_dir / "deployments"
    deploy_dir.mkdir()
    (deploy_dir / "production.dsl").write_text(
        'deploymentProduction = deploymentEnvironment "Production" {\n'
        '    deploymentNodeProductionCloud = deploymentNode "Azure Cloud" {\n'
        '        deploymentNode "rg-prod" "" "Resource Group" {\n'
        "            containerInstance containerBackendApi\n"
        "            containerInstance containerBackendDb\n"
        "            containerInstance containerFrontendUi\n"
        "        }\n"
        "    }\n"
        "}\n",
        encoding="utf-8",
    )

    views_dir = users_dir / "views"
    views_dir.mkdir()

    return ws


# ---------------------------------------------------------------------------
# Parsing tests
# ---------------------------------------------------------------------------

class TestParseUsers:
    def test_parses_users(self, sample_workspace: Path) -> None:
        users = _parse_users(sample_workspace)
        assert len(users) == 2
        assert users[0].var_name == "userAlice"
        assert users[0].display_name == "Alice"
        assert users[1].var_name == "userBob"

    def test_missing_file_returns_empty(self, tmp_path: Path) -> None:
        assert _parse_users(tmp_path) == []


class TestParseGroups:
    def test_parses_groups_and_systems(self, sample_workspace: Path) -> None:
        groups = _parse_groups(sample_workspace)
        assert len(groups) == 2

        eng = next(g for g in groups if g.display_name == "Engineering")
        assert len(eng.systems) == 2

        backend = next(s for s in eng.systems if s.var_name == "softwareSystemBackend")
        assert backend.has_containers is True
        assert "userAlice" in backend.user_var_names
        assert backend.group_name == "Engineering"

        frontend = next(s for s in eng.systems if s.var_name == "softwareSystemFrontend")
        assert "userBob" in frontend.user_var_names

    def test_system_without_containers(self, sample_workspace: Path) -> None:
        groups = _parse_groups(sample_workspace)
        ext = next(g for g in groups if g.display_name == "External")
        email = ext.systems[0]
        assert email.has_containers is False
        assert email.user_var_names == []

    def test_missing_dir_returns_empty(self, tmp_path: Path) -> None:
        assert _parse_groups(tmp_path) == []


class TestParseDeployments:
    def test_parses_environments_and_zones(self, sample_workspace: Path) -> None:
        envs = _parse_deployments(sample_workspace)
        assert len(envs) == 1
        env = envs[0]
        assert env.var_name == "deploymentProduction"
        assert env.display_name == "Production"
        assert len(env.zones) == 1
        assert env.zones[0].var_name == "deploymentNodeProductionCloud"

    def test_resolve_deployed_systems(self, sample_workspace: Path) -> None:
        groups = _parse_groups(sample_workspace)
        envs = _parse_deployments(sample_workspace)
        _resolve_deployed_systems(envs, groups)
        assert "softwareSystemBackend" in envs[0].system_var_names
        assert "softwareSystemFrontend" in envs[0].system_var_names


# ---------------------------------------------------------------------------
# View generation tests
# ---------------------------------------------------------------------------

class TestGenerateLandscapeViews:
    def test_contains_full_landscape(self, sample_workspace: Path) -> None:
        users = _parse_users(sample_workspace)
        groups = _parse_groups(sample_workspace)
        text, keys = _generate_landscape_views(users, groups)
        assert "SystemLandscape" in keys
        assert 'systemlandscape "SystemLandscape"' in text
        assert "include *" in text

    def test_contains_systems_only_view(self, sample_workspace: Path) -> None:
        users = _parse_users(sample_workspace)
        groups = _parse_groups(sample_workspace)
        text, keys = _generate_landscape_views(users, groups)
        assert "SystemLandscapeSoftwareSystems" in keys
        assert "softwareSystemBackend" in text
        assert "softwareSystemEmail" in text

    def test_contains_per_group_view(self, sample_workspace: Path) -> None:
        users = _parse_users(sample_workspace)
        groups = _parse_groups(sample_workspace)
        text, keys = _generate_landscape_views(users, groups)
        assert "SystemLandscapeEngineering" in keys
        # Group view should include interacting users
        # Find the Engineering group section
        assert "userAlice" in text
        assert "userBob" in text

    def test_contains_per_user_view(self, sample_workspace: Path) -> None:
        users = _parse_users(sample_workspace)
        groups = _parse_groups(sample_workspace)
        text, keys = _generate_landscape_views(users, groups)
        assert "SystemLandscapeUserAlice" in keys
        assert "SystemLandscapeUserBob" in keys

    def test_contains_users_only_view(self, sample_workspace: Path) -> None:
        users = _parse_users(sample_workspace)
        groups = _parse_groups(sample_workspace)
        text, keys = _generate_landscape_views(users, groups)
        assert "SystemLandscapeUsers" in keys

    def test_auto_generated_comments(self, sample_workspace: Path) -> None:
        users = _parse_users(sample_workspace)
        groups = _parse_groups(sample_workspace)
        text, _ = _generate_landscape_views(users, groups)
        assert "# [auto-generated]" in text


class TestGenerateSystemContextViews:
    def test_one_per_system(self, sample_workspace: Path) -> None:
        groups = _parse_groups(sample_workspace)
        text, keys = _generate_system_context_views(groups)
        assert "SystemContextBackend" in keys
        assert "SystemContextFrontend" in keys
        assert "SystemContextEmail" in keys

    def test_format(self, sample_workspace: Path) -> None:
        groups = _parse_groups(sample_workspace)
        text, _ = _generate_system_context_views(groups)
        assert 'systemContext softwareSystemBackend "SystemContextBackend"' in text
        assert "include *" in text
        assert "autoLayout" in text


class TestGenerateContainerViews:
    def test_only_systems_with_containers(self, sample_workspace: Path) -> None:
        groups = _parse_groups(sample_workspace)
        text, keys = _generate_container_views(groups)
        assert "ContainerBackend" in keys
        assert "ContainerFrontend" in keys
        # Email has no containers
        assert "ContainerEmailService" not in keys

    def test_format(self, sample_workspace: Path) -> None:
        groups = _parse_groups(sample_workspace)
        text, _ = _generate_container_views(groups)
        assert 'container softwareSystemBackend "ContainerBackend"' in text


class TestGenerateDeploymentViews:
    def test_zone_views(self, sample_workspace: Path) -> None:
        groups = _parse_groups(sample_workspace)
        envs = _parse_deployments(sample_workspace)
        _resolve_deployed_systems(envs, groups)
        text, keys = _generate_deployment_views(envs)
        assert "DeploymentProductionCloud" in keys

    def test_per_system_views(self, sample_workspace: Path) -> None:
        groups = _parse_groups(sample_workspace)
        envs = _parse_deployments(sample_workspace)
        _resolve_deployed_systems(envs, groups)
        text, keys = _generate_deployment_views(envs)
        assert "DeploymentProductionBackend" in keys
        assert "DeploymentProductionFrontend" in keys


# ---------------------------------------------------------------------------
# Integration test
# ---------------------------------------------------------------------------

class TestGenerateViewsIntegration:
    def test_generates_file(self, sample_workspace: Path) -> None:
        result = generate_views(sample_workspace)
        assert result is not None
        assert result.name == "_auto_generated_views.dsl"
        assert result.exists()

        content = result.read_text(encoding="utf-8")
        assert "AUTO-GENERATED VIEWS" in content
        assert "SystemLandscape" in content
        assert "SystemContext" in content
        assert "Container" in content

    def test_conflict_detection(self, sample_workspace: Path) -> None:
        """Hand-written views should take priority."""
        views_dir = sample_workspace / "workspace-includes" / "views"
        (views_dir / "custom.dsl").write_text(
            'systemlandscape "SystemLandscape" {\n    include *\n    autoLayout\n}\n',
            encoding="utf-8",
        )
        result = generate_views(sample_workspace)
        assert result is not None
        content = result.read_text(encoding="utf-8")
        # The auto-generated file should NOT contain SystemLandscape view
        # since it's already defined in custom.dsl
        lines_with_key = [line for line in content.split("\n") if '"SystemLandscape"' in line and "{" in line]
        assert len(lines_with_key) == 0

    def test_example_workspace(self) -> None:
        """Run against the real example workspace (monolithic DSL)."""
        example_dir = Path(__file__).resolve().parent.parent / "example"
        if not (example_dir / "workspace.dsl").exists():
            pytest.skip("Example workspace not available")

        result = generate_views(example_dir)
        assert result is not None
        content = result.read_text(encoding="utf-8")

        # Should have the header and section markers
        assert "AUTO-GENERATED VIEWS" in content
        assert "System Landscape Views" in content
        assert "System Context Views" in content
        assert "Container Views" in content

        # Clean up
        result.unlink()


# ---------------------------------------------------------------------------
# Monolithic DSL parsing
# ---------------------------------------------------------------------------


class TestParseMonolithicDsl:
    @pytest.fixture()
    def monolithic_workspace(self, tmp_path: Path) -> Path:
        dsl = '''\
workspace "Test" {
    model {
        alice = person "Alice"
        bob = person "Bob"

        group "Core" {
            backend = softwaresystem "Backend" "Main API" {
                api = container "API" "REST API"
            }
            frontend = softwaresystem "Frontend" "UI"
        }

        alice -> backend "Uses"
        bob -> frontend "Uses"
        bob -> backend "Also uses"

        deploymentEnvironment "Production" {
            deploymentNode "Cloud" {
                softwareSystemInstance backend
            }
        }
    }

    views {
        systemlandscape "SystemLandscape" {
            include *
            autoLayout
        }
    }
}
'''
        (tmp_path / "workspace.dsl").write_text(dsl, encoding="utf-8")
        return tmp_path

    def test_parses_users(self, monolithic_workspace: Path) -> None:
        users, _, _ = _parse_monolithic_dsl(monolithic_workspace)
        assert len(users) == 2
        assert users[0].var_name == "alice"
        assert users[1].display_name == "Bob"

    def test_parses_groups_and_systems(self, monolithic_workspace: Path) -> None:
        _, groups, _ = _parse_monolithic_dsl(monolithic_workspace)
        assert len(groups) == 1
        assert groups[0].display_name == "Core"
        assert len(groups[0].systems) == 2

    def test_system_with_containers(self, monolithic_workspace: Path) -> None:
        _, groups, _ = _parse_monolithic_dsl(monolithic_workspace)
        backend = next(s for s in groups[0].systems if s.var_name == "backend")
        assert backend.has_containers is True

    def test_system_without_containers(self, monolithic_workspace: Path) -> None:
        _, groups, _ = _parse_monolithic_dsl(monolithic_workspace)
        frontend = next(s for s in groups[0].systems if s.var_name == "frontend")
        assert frontend.has_containers is False

    def test_user_relationships(self, monolithic_workspace: Path) -> None:
        _, groups, _ = _parse_monolithic_dsl(monolithic_workspace)
        backend = next(s for s in groups[0].systems if s.var_name == "backend")
        frontend = next(s for s in groups[0].systems if s.var_name == "frontend")
        assert "alice" in backend.user_var_names
        assert "bob" in backend.user_var_names
        assert "bob" in frontend.user_var_names

    def test_deployments(self, monolithic_workspace: Path) -> None:
        _, _, envs = _parse_monolithic_dsl(monolithic_workspace)
        assert len(envs) == 1
        assert envs[0].display_name == "Production"
        assert "backend" in envs[0].system_var_names

    def test_generate_views_uses_monolithic_fallback(self, monolithic_workspace: Path) -> None:
        result = generate_views(monolithic_workspace)
        assert result is not None
        content = result.read_text(encoding="utf-8")

        # Per-user landscape views should be generated
        assert "SystemLandscapeUserAlice" in content
        assert "SystemLandscapeUserBob" in content

        # Hand-written SystemLandscape should be skipped
        lines = [line for line in content.split("\n") if '"SystemLandscape"' in line and "{" in line]
        assert len(lines) == 0

        # Clean up
        result.unlink()


# ---------------------------------------------------------------------------
# Nested groups and view keys
# ---------------------------------------------------------------------------

NESTED_MONOLITHIC = (
    "workspace {\n"
    "    model {\n"
    "        properties {\n"
    '            "structurizr.groupSeparator" "/"\n'
    "        }\n"
    '        group "Outer" {\n'
    '            api = softwareSystem "API"\n'
    '            group "Inner" {\n'
    '                web = softwareSystem "Web" {\n'
    '                    webApp = container "Web App"\n'
    "                }\n"
    "            }\n"
    "        }\n"
    "    }\n"
    "}\n"
)


def _systems_by_group(groups: list[DslGroup]) -> dict[str, list[str]]:
    return {g.display_name: [s.var_name for s in g.systems] for g in groups}


class TestNestedGroups:
    def test_monolithic_system_belongs_to_innermost_group(self, tmp_path: Path) -> None:
        (tmp_path / "workspace.dsl").write_text(NESTED_MONOLITHIC, encoding="utf-8")
        _, groups, _ = _parse_monolithic_dsl(tmp_path)
        assert _systems_by_group(groups) == {"Outer": ["api"], "Outer/Inner": ["web"]}

    def test_monolithic_view_keys_are_unique(self, tmp_path: Path) -> None:
        (tmp_path / "workspace.dsl").write_text(NESTED_MONOLITHIC, encoding="utf-8")
        text = generate_views(tmp_path).read_text(encoding="utf-8")
        keys = re.findall(r'"(\w+)" \{', text)
        assert len(keys) == len(set(keys))
        assert {"SystemContextWeb", "ContainerWeb", "SystemLandscapeOuterInner"} <= set(keys)

    def test_custom_separator(self, tmp_path: Path) -> None:
        dsl = NESTED_MONOLITHIC.replace('"structurizr.groupSeparator" "/"', '"structurizr.groupSeparator" "|"')
        (tmp_path / "workspace.dsl").write_text(dsl, encoding="utf-8")
        _, groups, _ = _parse_monolithic_dsl(tmp_path)
        assert "Outer|Inner" in _systems_by_group(groups)

    def test_container_groups_are_not_system_groups(self, tmp_path: Path) -> None:
        dsl = NESTED_MONOLITHIC.replace(
            'webApp = container "Web App"',
            'group "Frontend" {\n                        webApp = container "Web App"\n                    }',
        )
        (tmp_path / "workspace.dsl").write_text(dsl, encoding="utf-8")
        _, groups, _ = _parse_monolithic_dsl(tmp_path)
        assert _systems_by_group(groups) == {"Outer": ["api"], "Outer/Inner": ["web"]}

    def test_modular_nested_group_systems_are_parsed(self, tmp_path: Path) -> None:
        groups_dir = tmp_path / "workspace-includes" / "groups"
        groups_dir.mkdir(parents=True)
        (groups_dir / "outer.dsl").write_text(
            'groupOuter = group "Outer" {\n'
            '    softwareSystemApi = softwareSystem "API" {\n'
            "    }\n"
            '    groupInner = group "Inner" {\n'
            '        softwareSystemWeb = softwareSystem "Web" {\n'
            '            containerWebApp = container "Web App" {\n'
            "            }\n"
            "        }\n"
            "    }\n"
            "}\n",
            encoding="utf-8",
        )
        groups = _parse_groups(tmp_path)
        assert _systems_by_group(groups) == {"Outer": ["softwareSystemApi"], "Outer/Inner": ["softwareSystemWeb"]}
        assert groups[1].systems[0].has_containers


class TestViewKeys:
    def test_keys_drop_punctuation_and_accents(self) -> None:
        system = DslSoftwareSystem("softwareSystemPay", "Pay", "Finance & Contrôle", False, ["userHr"])
        users = [DslUser("userHr", "HR (Payroll)")]
        groups = [DslGroup("groupFinance", "Finance & Contrôle", systems=[system])]
        _, keys = _generate_landscape_views(users, groups)
        assert "SystemLandscapeFinanceControle" in keys
        assert "SystemLandscapeUserHRPayroll" in keys

    def test_name_without_latin_letters_gets_no_view(self) -> None:
        system = DslSoftwareSystem("softwareSystemPay", "Pay", "Платежи", False)
        groups = [DslGroup("groupPay", "Платежи", systems=[system])]
        _, keys = _generate_landscape_views([], groups)
        assert keys.count("SystemLandscape") == 1
        assert all(re.fullmatch(r"[A-Za-z0-9]+", k) for k in keys), keys

    def test_deployment_keys_drop_punctuation(self) -> None:
        env = DslDeploymentEnvironment(
            var_name="Prod", display_name="Production (EU)",
            zones=[DslDeploymentZone("Zone", "Azure / West")],
        )
        _, keys = _generate_deployment_views([env])
        assert keys == ["DeploymentProductionEUAzureWest"]
