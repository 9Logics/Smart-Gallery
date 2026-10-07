import re

with open('app/static/js/globals.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the early return with just letting it continue without caching, OR wrap it
new_fetch = '''var originalFetch = window.fetch;
window.fetch = async (...args) => {
    const request = new Request(...args);
    const isCacheable = (request.method === 'GET' && request.url.includes('/api/') && !request.url.includes('/api/photo/file') && !request.url.includes('/api/photo/thumbnail'));
    
    if (['POST', 'PUT', 'DELETE'].includes(request.method)) {
        sessionStorage.clear();
    }
    
    const cacheKey = 'imgfinder_v2_' + request.url;
    if (isCacheable) {
        const cachedResponse = sessionStorage.getItem(cacheKey);
        if (cachedResponse) {
            try {
                const data = JSON.parse(cachedResponse);
                return new Response(JSON.stringify(data), {
                    status: 200,
                    headers: { 'Content-Type': 'application/json' }
                });
            } catch (e) {
                sessionStorage.removeItem(cacheKey);
            }
        }
    }

    let response;
    try {
        response = await originalFetch(...args);
    } catch(e) {
        throw e;
    }
    
    if (response.status === 423) {
        try {
            const data = await response.clone().json();
            if (data && data.error && window.appAlert) {
                window.appAlert(data.error);
            }
        } catch(e) {}
    }

    if (isCacheable && response.ok && response.headers.get('content-type')?.includes('application/json')) {
        const clone = response.clone();
        try {
            const text = await clone.text();
            sessionStorage.setItem(cacheKey, text);
        } catch(e) {}
    }
    
    return response;
};'''

pattern = r"var originalFetch = window\.fetch;.*?return response;\s*\};"
content = re.sub(pattern, new_fetch, content, flags=re.DOTALL)

with open('app/static/js/globals.js', 'w', encoding='utf-8') as f:
    f.write(content)
