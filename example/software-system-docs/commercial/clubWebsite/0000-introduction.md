# Description

Official BelFoot FC public website serving as the primary digital presence for the club, providing news, match fixtures, squad profiles, and media content to fans and the general public.

# Business Capabilities

- Publish and manage club news articles and press releases
- Display match fixtures, results, and league standings
- Present first team and academy squad profiles
- Host media galleries and video content
- Provide club information, history, and contact details

# Bounded Context
- Fan Engagement & Communications

# Data Landscape

| Entity | Description | Role | Software Systems |
|--------|-------------|------|------------------|
| [Article](ARTICLE) | Published content piece on the club website | Owns | |
| [Fixture](FIXTURE) | Scheduled match or event in the calendar | Owns | |
| [Squad Profile](SQUAD_PROFILE) | Public-facing profile of a player in the squad | Owns | |
| [Media Asset](MEDIA_ASSET) | Photo, video, or graphic used in content | Owns | |
| [Match Result](MATCH_RESULT) | Final score and outcome of a completed match | Uses | -- |
| [League Standing](LEAGUE_STANDING) | Team's position in the league table | Uses | -- |
