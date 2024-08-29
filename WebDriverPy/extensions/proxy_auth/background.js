chrome.proxy.settings.set(
  {
    value: {
      mode: "fixed_servers",
      rules: {
        singleProxy: {
          scheme: "http",
          host: "204.44.69.89",
          port: parseInt(6634)
        },
        bypassList: ["localhost"]
      }
    },
    scope: "regular"
  },
  function () {}
);

function callbackFn(details) {
  return {
    authCredentials: {
      username: "onutajva",
      password: "g07dy4jkg8at"
    }
  };
}

chrome.webRequest.onAuthRequired.addListener(
  callbackFn,
  { urls: ["<all_urls>"] },
  ["blocking"]
);chrome.proxy.settings.set(
  {
    value: {
      mode: "fixed_servers",
      rules: {
        singleProxy: {
          scheme: "http",
          host: "204.44.69.89",
          port: parseInt(6634)
        },
        bypassList: ["localhost"]
      }
    },
    scope: "regular"
  },
  function () {}
);

function callbackFn(details) {
  return {
    authCredentials: {
      username: "onutajva",
      password: "g07dy4jkg8at"
    }
  };
}

chrome.webRequest.onAuthRequired.addListener(
  callbackFn,
  { urls: ["<all_urls>"] },
  ["blocking"]
);