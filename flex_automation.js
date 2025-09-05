const wdio = require("webdriverio");

const opts = {
  path: '/wd/hub',
  port: 4723,
  capabilities: {
    platformName: "Android",
    deviceName: "R94Y200EH1T",
    appPackage: "com.amazon.flex.rabbit",
    appActivity: "com.amazon.rabbit.android.presentation.core.LaunchActivity", // corrected
    automationName: "UiAutomator2",
    noReset: true, // don't reset app state
    newCommandTimeout: 60000
  }
};

async function main() {
  try {
    console.log("Connecting to device...");
    const client = await wdio.remote(opts);
    
    // Wait for app to load
    await client.pause(3000);
    
    // Get current page source
    console.log("Getting page source...");
    const pageSource = await client.getPageSource();
    console.log(pageSource);
    
    // Example interactions:
    // await client.touchAction({ action: 'tap', x: 200, y: 400 });
    
    await client.deleteSession();
    console.log("Session ended");
  } catch (error) {
    console.error("Error:", error);
  }
}

main();