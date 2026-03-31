const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const mlDir = __dirname;
const venvDir = path.join(mlDir, 'venv');

let pythonCmd;
if (process.platform === 'win32') {
    pythonCmd = path.join(venvDir, 'Scripts', 'python.exe');
} else {
    pythonCmd = path.join(venvDir, 'bin', 'python');
}

// Check if venv exists
if (!fs.existsSync(pythonCmd)) {
    console.error('❌ Virtual environment not found for ML service.');
    console.error('Please run: npm run setup:ml && npm run setup:ml:install');
    process.exit(1);
}

// Check if best.pt exists
if (!fs.existsSync(path.join(mlDir, 'best.pt'))) {
    console.warn('⚠️  Warning: best.pt model file not found in', mlDir);
}

console.log('🚀 Starting FastAPI ML service on http://localhost:5000...');

const mlProcess = spawn(pythonCmd, ['ml.py'], {
    cwd: mlDir,
    stdio: 'inherit',
    shell: false
});

mlProcess.on('error', (err) => {
    console.error('❌ Failed to start ML service:', err);
    process.exit(1);
});

mlProcess.on('exit', (code) => {
    if (code !== 0) {
        console.log(`⚠️  ML service exited with code ${code}`);
    }
    process.exit(code);
});

// Handle Ctrl+C gracefully
process.on('SIGINT', () => {
    console.log('\n🛑 Stopping ML service...');
    mlProcess.kill('SIGINT');
});

process.on('SIGTERM', () => {
    mlProcess.kill('SIGTERM');
});