
// JavaScript Logging Example

// Function to log messages
function logMessage(level, message) {
    console.log(`[${level}] ${message}`);
}

// Log some messages
logMessage('INFO', 'Starting JavaScript example');
logMessage('DEBUG', 'Initializing variables');

// Simulate an error
try {
    throw new Error('Example error');
} catch (error) {
    logMessage('ERROR', `Caught error: ${error.message}`);
}

logMessage('INFO', 'JavaScript example completed');
