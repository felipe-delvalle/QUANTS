/**
 * Client-side logging utility for debugging modal and click handler issues
 * Sends logs to backend API endpoint and falls back to console
 */

class ClientLogger {
  constructor() {
    this.logQueue = [];
    this.flushInterval = 2000; // Flush logs every 2 seconds
    this.maxQueueSize = 50; // Max logs before forced flush
    this.flushTimer = null;
    this.enabled = true;
    this.apiEndpoint = '/api/logs';
    
    // Start flush timer
    this.startFlushTimer();
    
    // Flush on page unload
    window.addEventListener('beforeunload', () => this.flush());
  }
  
  /**
   * Log a message
   * @param {string} level - Log level (DEBUG, INFO, WARN, ERROR)
   * @param {string} source - Source component (click_handler, modal, etc.)
   * @param {string} event - Event name
   * @param {object} data - Additional data
   * @param {Error} error - Error object if any
   */
  log(level, source, event, data = {}, error = null) {
    if (!this.enabled) return;
    
    const logEntry = {
      timestamp: new Date().toISOString(),
      level: level,
      source: source,
      event: event,
      data: data,
      error: error ? {
        message: error.message,
        stack: error.stack,
        name: error.name
      } : null,
      user_agent: navigator.userAgent,
      url: window.location.pathname + window.location.search
    };
    
    // Always log to console for immediate feedback
    const consoleMethod = level === 'ERROR' ? 'error' : 
                         level === 'WARN' ? 'warn' : 
                         level === 'DEBUG' ? 'debug' : 'log';
    console[consoleMethod](`[${level}] [${source}] ${event}`, data, error || '');
    
    // Add to queue
    this.logQueue.push(logEntry);
    
    // Force flush if queue is too large or if it's an error
    if (this.logQueue.length >= this.maxQueueSize || level === 'ERROR') {
      this.flush();
    }
  }
  
  /**
   * Convenience methods
   */
  debug(source, event, data) {
    this.log('DEBUG', source, event, data);
  }
  
  info(source, event, data) {
    this.log('INFO', source, event, data);
  }
  
  warn(source, event, data) {
    this.log('WARN', source, event, data);
  }
  
  error(source, event, data, error) {
    this.log('ERROR', source, event, data, error);
  }
  
  /**
   * Start automatic flush timer
   */
  startFlushTimer() {
    if (this.flushTimer) {
      clearInterval(this.flushTimer);
    }
    this.flushTimer = setInterval(() => {
      if (this.logQueue.length > 0) {
        this.flush();
      }
    }, this.flushInterval);
  }
  
  /**
   * Flush logs to backend
   */
  flush() {
    if (this.logQueue.length === 0) return;
    
    const logsToSend = [...this.logQueue];
    this.logQueue = [];
    
    // Send to backend
    fetch(this.apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ logs: logsToSend })
    }).catch(err => {
      // If API fails, log to console only
      console.error('Failed to send logs to backend:', err);
      // Re-queue logs for next attempt (but limit to prevent memory issues)
      if (this.logQueue.length < this.maxQueueSize) {
        this.logQueue.unshift(...logsToSend);
      }
    });
  }
  
  /**
   * Disable logging
   */
  disable() {
    this.enabled = false;
    this.flush(); // Flush any pending logs
  }
  
  /**
   * Enable logging
   */
  enable() {
    this.enabled = true;
  }
}

// Create global logger instance
window.clientLogger = new ClientLogger();

// Export for module systems (if needed)
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ClientLogger;
}
