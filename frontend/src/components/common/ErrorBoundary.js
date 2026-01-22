import React from 'react';
import Alert from './Alert';
import Button from './Button';

/**
 * ErrorBoundary component
 * Catches JavaScript errors in child components
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error,
      errorInfo
    });

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // Here you could also send the error to an error reporting service
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });

    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="container mt-4">
          <Alert variant="danger">
            <Alert.Heading>
              <i className="bi bi-exclamation-triangle me-2" />
              Something went wrong
            </Alert.Heading>
            <p>
              {this.props.errorMessage || 'An unexpected error occurred. Please try refreshing the page.'}
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mt-3">
                <summary style={{ cursor: 'pointer' }}>Error details</summary>
                <pre className="mt-2 p-2 bg-light border rounded" style={{ fontSize: '0.85rem' }}>
                  {this.state.error.toString()}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}

            <div className="mt-3">
              <Button variant="primary" onClick={this.handleReset} className="me-2">
                Try Again
              </Button>
              <Button
                variant="outline-secondary"
                onClick={() => window.location.reload()}
              >
                Reload Page
              </Button>
            </div>
          </Alert>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
