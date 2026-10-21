pluginManagement { repositories { maven { url = uri("offline-maven"); metadataSources { mavenPom(); gradleMetadata() } } } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS); repositories { maven { url = uri("offline-maven"); metadataSources { mavenPom(); gradleMetadata() } } } }
rootProject.name = "VideoKitD1InputSink05"
include(":app")
