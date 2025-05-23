// Show notification
function showNotification(message, type = 'info') {
    // Don't show empty notifications
    if (!message || message.trim() === '') {
        console.warn('Attempted to show empty notification');
        return;
    }
    
    // Don't show API request notifications
    if (message.includes('GET /api/') || message.includes('POST /api/')) {
        console.debug('Skipping API request notification:', message);
        return;
    }
    
    // Clear existing notifications of the same type
    const existingNotifications = elements.notificationArea.querySelectorAll(`.notification.${type}`);
    existingNotifications.forEach(notification => {
        notification.remove();
    });
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    // Create notification content
    const content = document.createElement('div');
    content.className = 'notification-content';
    content.innerHTML = `<strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}`;
    
    // Add content to notification
    notification.appendChild(content);
    
    // Add notification to notification area
    elements.notificationArea.appendChild(notification);
    
    // Remove notification after a delay
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
}
