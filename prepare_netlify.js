const fs = require('fs-extra');
const path = require('path');

// Create dist directory if it doesn't exist
if (!fs.existsSync('ui/dist')) {
  fs.mkdirSync('ui/dist', { recursive: true });
}

// Copy templates to dist
fs.copySync('ui/templates', 'ui/dist');

// Copy static files to dist
fs.copySync('ui/static', 'ui/dist/static');

console.log('Files prepared for Netlify deployment');
