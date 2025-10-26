const http = require('http');
const url = process.argv[2] || 'http://localhost:3000/search';

console.log(`Fetching ${url} ...`);
http.get(url, (res) => {
  let body = '';
  res.setEncoding('utf8');
  res.on('data', (chunk) => body += chunk);
  res.on('end', () => {
    if (body.includes('id="ls-search-input"')) {
      console.log('OK: search page contains input wrapper id');
      process.exit(0);
    } else {
      console.error('FAIL: input wrapper id not found in /search');
      process.exit(2);
    }
  });
}).on('error', (err) => {
  console.error('Error fetching URL:', err.message);
  process.exit(3);
});
