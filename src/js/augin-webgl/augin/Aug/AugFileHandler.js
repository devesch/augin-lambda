import { unzipSync, strFromU8 } from '../../threejs/jsm/libs/fflate.module.js';

const CACHE_NAME = 'augin-cache';

export class AugFileHandler {
    constructor(url, id, progressCallback = null) {
        this.identifier = id;
        if (this.identifier === void 0)
            this.identifier = url;
        if (progressCallback === null) {
            return this.fetchWithoutProgress(url);
        }
        return this.fetchWithProgress(url, progressCallback);
    }

    fetchWithoutProgress(url) {
        const scope = this;
        return new Promise(function (resolve, reject) {
            fetch(url)
                .then(response => {
                    // Check if the request was successful
                    if (!response.ok) {
                        reject('Network response was not ok');
                    }
                    // Get the data from the response
                    return response.arrayBuffer();
                })
                .then(buffer => {
                    scope.file = new Uint8Array(buffer);
                    resolve(scope);
                })
                .catch(reject);
        });
    }

    fetchWithProgress(url, progressCallback) {
        const scope = this;
        return new Promise(async (resolve, reject) => {
            scope.file = await scope.retrieveCachedBytes();
            if (scope.file != null) {
                resolve(scope);
                return;
            }
            fetch(url).then(response => {
                if (!response.ok) {
                    reject(`Error fetching ${url}: ${response.statusText}`);
                }

                const reader = response.body.getReader();
                const contentLength = +response.headers.get('Content-Length');
                let receivedLength = 0;
                const chunks = [];

                reader.read().then(async function processChunk({ done, value }) {
                    if (done) {
                        let chunksAll = new Uint8Array(receivedLength); // (4.1)
                        let position = 0;
                        for (let chunk of chunks) {
                            chunksAll.set(chunk, position);
                            position += chunk.length;
                        }
                        scope.file = new Uint8Array(chunksAll.buffer);
                        await scope.cacheBytes(scope.file);
                        resolve(scope);
                        return;
                    }

                    chunks.push(value);
                    receivedLength += value.length;

                    progressCallback(receivedLength / contentLength);
                    reader.read().then(processChunk);
                });
            }).catch(reject);
        });
    }

    async cacheBytes(byteArray) {
        try {
            // Create a new Response object with the bytes
            const response = new Response(byteArray);

            // Open or create a cache with a specific name
            const cache = await caches.open(CACHE_NAME);

            // Store the response in the cache
            await cache.put(this.identifier, response);
        } catch (error) {
            console.error('Caching failed:', error);
        }
    }

    async retrieveCachedBytes() {
        try {
            // Open the cache with a specific name
            const cache = await caches.open(CACHE_NAME);

            // Retrieve the cached response
            const response = await cache.match(this.identifier);

            if (response) {
                // Read the bytes from the response
                const buffer = await response.arrayBuffer();
                const byteArray = new Uint8Array(buffer)
                return byteArray;
            } else {
                console.log('File not found in cache', this.identifier);
                return null;
            }
        } catch (error) {
            console.error('Cache retrieval failed:', error);
            return null;
        }
    }

    async clearCache() {
        try {
            // Open the cache
            const cache = await caches.open(CACHE_NAME);

            // Check if the URL is cached
            const cachedResponse = await cache.match(this.identifier);

            // Delete the cached response if found
            if (cachedResponse) {
                await cache.delete(this.identifier);
            } else {
                console.log(`Cache not found: ${this.identifier}`);
            }
        } catch (error) {
            console.error('Cache clearing failed:', error);
        }
    }

    unzip() {
        const zip = unzipSync(this.file);

        const files = {};
        for (const filename in zip) {
            const fileData = zip[filename].buffer;
            const extension = filename.endsWith('.aug') ? '.aug' : filename.endsWith('.in') ? '.in' : '.clj';
            files[extension] = fileData;
        }
        return files;
    }
}