module.exports = {
  expo: {
    name: "AmazonFlexFrontend",
    slug: "amazon-flex-frontend",
    version: "1.0.0",
    platforms: ["ios", "android", "web"],
    orientation: "portrait",
    icon: "./assets/icon.png",
    splash: {
      image: "./assets/splash.png",
      resizeMode: "contain",
      backgroundColor: "#ffffff",
    },
    updates: {
      fallbackToCacheTimeout: 0,
    },
    assetBundlePatterns: ["**/*"],
    ios: {
      supportsTablet: true,
    },
    android: {
      package: "com.onyae.amazonflexfrontend",
      adaptiveIcon: {
        foregroundImage: "./assets/adaptive-icon.png",
        backgroundColor: "#ffffff",
      },
    },
    web: {
      favicon: "./assets/favicon.png",
    },
    extra: {
      eas: {
        projectId: "601485b8-55ac-49e3-9b70-c06b317e8bdd", // Add this line
      },
    },
  },
};