pluginManagement { repositories { maven { url = uri("offline-maven") }; google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { maven { url = uri("offline-maven") }; google(); mavenCentral() } }
rootProject.name = "VideoKitD1Render01"
include(":app")
