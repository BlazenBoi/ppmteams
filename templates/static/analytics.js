function analytics() {
    var canvas = document.getElementById("myTestCanvas");
    var gl = canvas.getContext("experimental-webgl");
    var debug = gl.getExtension('WEBGL_debug_renderer_info');
    const userjson = {"path":window.location.pathname, "agent":window.navigator.userAgent, "platform":window.navigator.platform, "depth":screen.colorDepth, "cookieEnabled":window.navigator.cookieEnabled, "tz":Intl.DateTimeFormat().resolvedOptions().timeZone, "lang":navigator.language, "product":window.navigator.product, "productsub":window.navigator.productSub, "vendor":window.navigator.vendor, "concurrency":window.navigator.hardwareConcurrency, "appCodeName":window.navigator.appCodeName, "appName":window.navigator.appName, "webGLRenderer":gl.getParameter(gl.RENDERER), "webGLVendor":gl.getParameter(gl.VENDOR), "webGLUVendor":gl.getParameter(debug.UNMASKED_VENDOR_WEBGL), "webGLURenderer":gl.getParameter(debug.UNMASKED_RENDERER_WEBGL)}
    fetch(`/analytics`, {
        method: "POST",
        credentials: "include",
        body: JSON.stringify(userjson),
        cache: "no-cache",
        headers: new Headers({
            "content-type": "application/json"
        })
    })
}

analytics();