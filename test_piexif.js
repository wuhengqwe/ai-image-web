// Test different JPEG data formats for piexif v2 insert/load
const piexif = require("./piexif.min.js");

// Create a minimal valid JPEG as base64
// Using a real 1x1 white JPEG
const b64data = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRofHh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwhMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYI4Q/SFhSRFJiMkVic4EzQjR0RSlFNkVUcCZS/2gAMAwEAAhEDEQA/AKqAP/Z";

// Convert to Uint8Array (same as browser's blob.arrayBuffer() -> new Uint8Array())
const binaryStr = atob(b64data);
const bytes = new Uint8Array(binaryStr.length);
for (let i = 0; i < binaryStr.length; i++) {
    bytes[i] = binaryStr.charCodeAt(i);
}

const exifObj = {
    "0th": {271: "Apple", 272: "iPhone 14 Pro"},
    "Exif": {34855: 100, 33437: [178, 100]},
    "GPS": {},
    "1st": {},
    "thumbnail": null
};

console.log("=== Test 1: Uint8Array ===");
try {
    const r = piexif.insert(exifObj, bytes);
    console.log("SUCCESS, length:", r.length);
} catch(e) {
    console.log("FAIL:", e.message.slice(0, 100));
}

console.log("\n=== Test 2: ArrayBuffer ===");
try {
    const r = piexif.insert(exifObj, bytes.buffer);
    console.log("SUCCESS, length:", r.length);
} catch(e) {
    console.log("FAIL:", e.message.slice(0, 100));
}

console.log("\n=== Test 3: base64 string ===");
try {
    const r = piexif.insert(exifObj, b64data);
    console.log("SUCCESS, length:", r.length);
} catch(e) {
    console.log("FAIL:", e.message.slice(0, 100));
}

console.log("\n=== Test 4: Node Buffer ===");
try {
    const buf = Buffer.from(b64data, 'base64');
    const r = piexif.insert(exifObj, buf);
    console.log("SUCCESS, length:", r.length);
} catch(e) {
    console.log("FAIL:", e.message.slice(0, 100));
}

// Test load function too
console.log("\n=== load with Uint8Array ===");
try {
    const loaded = piexif.load(bytes);
    console.log("SUCCESS:", JSON.stringify(loaded).slice(0, 100));
} catch(e) {
    console.log("FAIL:", e.message.slice(0, 100));
}

console.log("\n=== load with Node Buffer ===");
try {
    const buf = Buffer.from(b64data, 'base64');
    const loaded2 = piexif.load(buf);
    console.log("SUCCESS:", JSON.stringify(loaded2).slice(0, 100));
} catch(e) {
    console.log("FAIL:", e.message.slice(0, 100));
}
