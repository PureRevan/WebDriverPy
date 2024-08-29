chrome.proxy.settings.set(
  {
    value: {
      mode: "fixed_servers",
      rules: {
        singleProxy: {
          scheme: "!__::SCHEME_TEMPLATE_DUMMY::__!",
          host: "!__::HOST_TEMPLATE_DUMMY::__!",
          port: parseInt(!__::PORT_TEMPLATE_DUMMY::__!)
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
      username: "!__::USERNAME_TEMPLATE_DUMMY::__!",
      password: "!__::PASSWORD_TEMPLATE_DUMMY::__!"
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
          scheme: "!__::SCHEME_TEMPLATE_DUMMY::__!",
          host: "!__::HOST_TEMPLATE_DUMMY::__!",
          port: parseInt(!__::PORT_TEMPLATE_DUMMY::__!)
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
      username: "!__::USERNAME_TEMPLATE_DUMMY::__!",
      password: "!__::PASSWORD_TEMPLATE_DUMMY::__!"
    }
  };
}

chrome.webRequest.onAuthRequired.addListener(
  callbackFn,
  { urls: ["<all_urls>"] },
  ["blocking"]
);