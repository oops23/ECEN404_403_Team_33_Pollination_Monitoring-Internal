const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const mlDir = __dirname;
const venvDir = path.join(mlDir, 'venv');

console.log('🔧 Setting up ML Python environment...\n');

// Check if venv exists
if (!fs.existsSync(venvDir)) {
    console.error('❌ Virtual environment not found.');
    console.error('Please run: npm run setup:ml');
    process.exit(1);
}

console.log('✅ Virtual environment found');

// Determine pip path (for WSL/Linux, always use bin/)
let pipCmd;
if (process.platform === 'win32') {
    pipCmd = path.join(venvDir, 'Scripts', 'pip.exe');
} else {
    pipCmd = path.join(venvDir, 'bin', 'pip');
}

// Verify pip exists
if (!fs.existsSync(pipCmd)) {
    console.error('❌ pip not found in virtual environment');
    console.error('Try deleting venv folder and running: npm run setup:ml again');
    process.exit(1);
}

// Upgrade pip first
console.log('📦 Upgrading pip...');
try {
    execSync(`"${pipCmd}" install --upgrade pip`, {
        cwd: mlDir,
        stdio: 'inherit'
    });
} catch (err) {
    console.warn('⚠️  Could not upgrade pip, continuing anyway...');
}

// Install requirements
console.log('📦 Installing Python packages (this may take a few minutes)...');
try {
    execSync(`"${pipCmd}" install -r requirements.txt`, {
        cwd: mlDir,
        stdio: 'inherit'
    });
    console.log('\n✅ Python packages installed successfully!');
    console.log('✅ ML setup complete! You can now run: npm run dev\n');
} catch (err) {
    console.error('❌ Failed to install Python packages');
    console.error('Check the error messages above for details');
    process.exit(1);
}