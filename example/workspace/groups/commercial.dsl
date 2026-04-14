groupCommercial = group "Commercial" {

    softwareSystemSalesforceCrm = softwareSystem "Salesforce CRM" "Customer Relationship Management for fan and sponsor interactions" "External System" {

        !docs ../../software-system-docs/commercial/salesforceCrm

        containerSalesforceCrmUi = container "Salesforce Lightning" "CRM interface for sales and support agents" "Salesforce Lightning" "CLOUD_RESOURCE" {
            userTicketingAgent -> this "Manage customer records"
        }

        containerSalesforceCrmApi = container "Salesforce REST API" "API for customer data integration" "Salesforce REST" "CLOUD_RESOURCE" {
        }

        containerSalesforceCrmUi -> containerSalesforceCrmApi "Query and update records" "JSON/HTTPS"
    }

    softwareSystemStripe = softwareSystem "Stripe" "Online payment processing platform" "External System" {

        !docs ../../software-system-docs/commercial/stripe

        containerStripeApi = container "Stripe Payments API" "Payment intents, refunds, and subscription management" "Stripe" "CLOUD_RESOURCE" {
        }
    }

    softwareSystemTicketingPlatform = softwareSystem "Ticketing Platform" "B2C and B2B ticket sales, season passes, and seat allocation" {

        !docs ../../software-system-docs/commercial/ticketingPlatform

        containerTicketingPlatformDatabase = container "Ticketing Database" "Tickets, events, seats, and season passes" "PostgreSQL" "DATASET" {
        }

        containerTicketingPlatformApi = container "Ticketing API" "Ticket sales, availability, and allocation management" "Node.js" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/ticketing-api"
            }
            this -> containerTicketingPlatformDatabase "Manage data" "SQL/TCP"
        }

        containerTicketingPlatformUi = container "Ticketing Portal" "Online ticket purchasing and season pass management" "React" "UI_ELEMENT" {
            userFan -> this "Purchase tickets and manage season passes"
            userSeasonTicketHolder -> this "View and manage season pass"
            userTicketingAgent -> this "Manage ticket allocations and sales"
            this -> containerTicketingPlatformApi "Manage tickets" "JSON/HTTPS"
            this -> containerEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemWebStore = softwareSystem "Web Store" "Online merchandise and memorabilia shop" {

        !docs ../../software-system-docs/commercial/webStore

        containerWebStoreDatabase = container "Web Store Database" "Products, orders, carts, and shipments" "PostgreSQL" "DATASET" {
        }

        containerWebStoreApi = container "Web Store API" "Product catalog, cart, checkout, and order management" "Node.js" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/webstore-api"
            }
            this -> containerWebStoreDatabase "Manage data" "SQL/TCP"
        }

        containerWebStoreUi = container "Web Store" "Public-facing merchandise shop" "Next.js" "WEBSITE" {
            userPublic -> this "Browse merchandise"
            userFan -> this "Purchase merchandise"
            userMerchandisingManager -> this "Manage product catalog"
            this -> containerWebStoreApi "Manage orders and products" "JSON/HTTPS"
        }
    }

    softwareSystemSponsorshipPortal = softwareSystem "Sponsorship Portal" "B2B partner and sponsor management platform" {

        !docs ../../software-system-docs/commercial/sponsorshipPortal

        containerSponsorshipPortalDatabase = container "Sponsorship Database" "Sponsors, contracts, campaigns, and hospitality packages" "PostgreSQL" "DATASET" {
        }

        containerSponsorshipPortalApi = container "Sponsorship API" "Partner onboarding, contract management, and campaign tracking" ".NET" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/sponsorship-api"
            }
            this -> containerSponsorshipPortalDatabase "Manage data" "SQL/TCP"
        }

        containerSponsorshipPortalUi = container "Sponsorship Portal" "Self-service portal for sponsors and partnership managers" "React" "UI_ELEMENT" {
            userSponsor -> this "Manage sponsorship agreements and view campaign results"
            this -> containerSponsorshipPortalApi "Manage sponsorships" "JSON/HTTPS"
            this -> containerEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemFanEngagement = softwareSystem "Fan Engagement Platform" "Loyalty program, push notifications, and gamification" {

        !docs ../../software-system-docs/commercial/fanEngagement

        containerFanEngagementDatabase = container "Fan Engagement Database" "Loyalty points, achievements, and fan profiles" "Azure Cosmos DB" "DATASET" {
        }

        containerFanEngagementApi = container "Fan Engagement API" "Loyalty points, gamification, and notification management" "Node.js" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/fan-engagement-api"
            }
            this -> containerFanEngagementDatabase "Manage data" "JSON/HTTPS"
        }

        containerFanEngagementApp = container "BelFoot Fan App" "Mobile app for loyalty, live match info, and fan engagement" "React Native" "APPLICATION" {
            userFan -> this "Check loyalty points and receive match day notifications"
            userSeasonTicketHolder -> this "Access exclusive content and digital season pass"
            this -> containerFanEngagementApi "Manage fan interactions" "JSON/HTTPS"
            this -> containerEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemProductDevelopment = softwareSystem "Product Development" "Product and service design, B2B offerings, and touchpoint management" {

        !docs ../../software-system-docs/commercial/productDevelopment

        containerProductDevelopmentDatabase = container "Product Development Database" "Product concepts, offerings, and touchpoint designs" "PostgreSQL" "DATASET" {
        }

        containerProductDevelopmentApi = container "Product Development API" "Product lifecycle, offering management, and touchpoint design" "Node.js" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/product-development-api"
            }
            this -> containerProductDevelopmentDatabase "Manage data" "SQL/TCP"
        }

        containerProductDevelopmentUi = container "Product Development Portal" "Product concept design and offering management" "React" "UI_ELEMENT" {
            userProductManager -> this "Design products and manage offerings"
            this -> containerProductDevelopmentApi "Manage products" "JSON/HTTPS"
            this -> containerEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemMarketingPlatform = softwareSystem "Marketing Platform" "Campaign management, brand activation, and content marketing" {

        !docs ../../software-system-docs/commercial/marketingPlatform

        containerMarketingPlatformDatabase = container "Marketing Database" "Campaigns, brand assets, and sponsorship programs" "PostgreSQL" "DATASET" {
        }

        containerMarketingPlatformApi = container "Marketing API" "Campaign orchestration, brand management, and content distribution" "Node.js" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/marketing-api"
            }
            this -> containerMarketingPlatformDatabase "Manage data" "SQL/TCP"
        }

        containerMarketingPlatformUi = container "Marketing Portal" "Campaign planning, brand asset management, and analytics" "React" "UI_ELEMENT" {
            userMarketingManager -> this "Plan campaigns and manage brand assets"
            this -> containerMarketingPlatformApi "Manage marketing" "JSON/HTTPS"
            this -> containerEntraIdApi "Authenticate" "JSON/HTTPS"
        }
    }

    softwareSystemClubWebsite = softwareSystem "Club Website" "Official BelFoot FC public website with news, fixtures, squad info, and media content" {

        !docs ../../software-system-docs/commercial/clubWebsite

        containerClubWebsiteDatabase = container "Club Website Database" "Articles, fixtures, squad profiles, and media assets" "PostgreSQL" "DATASET" {
        }

        containerClubWebsiteCms = container "Club Website CMS" "Content management for news, media, and editorial workflows" "Node.js" "SERVICE" {
            properties {
                "Repository" "https://dev.azure.com/BelFoot/_git/club-website-cms"
            }
            this -> containerClubWebsiteDatabase "Manage data" "SQL/TCP"
        }

        containerClubWebsiteUi = container "Club Website" "Public-facing club website with news, fixtures, and squad information" "Next.js" "WEBSITE" {
            userPublic -> this "Browse club news, fixtures, and squad info"
            userFan -> this "Read news and check match schedules"
            userCommunicationsManager -> this "Publish news articles and media content"
            this -> containerClubWebsiteCms "Fetch and manage content" "JSON/HTTPS"
        }
    }
}
