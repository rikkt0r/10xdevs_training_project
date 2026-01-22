import React from 'react';
import { Container } from 'react-bootstrap';
import Alert from './Alert';
import Button from './Button';

/**
 * ErrorBoundary component
 * Catches JavaScript errors anywhere in the component tree
 * Supports multiple levels: app, route, widget
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error,
      errorInfo,
    });

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('ErrorBoundary caught an error:', error, errorInfo);
    }

    // Call optional onError callback
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });

    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  renderAppLevelError() {
    return (
      <Container className="mt-5">
        <div className="text-center">
          <div className="mb-4">
            <i className="bi bi-exclamation-triangle text-danger" style={{ fontSize: '4rem' }} />
          </div>
          <h1 className="mb-3">Oops! Something went wrong</h1>
          <p className="text-muted mb-4">
            We're sorry, but an unexpected error occurred. Please try refreshing the page.
          </p>
          <div className="d-flex gap-2 justify-content-center">
            <Button variant="primary" onClick={() => window.location.reload()}>
              <i className="bi bi-arrow-clockwise me-2" />
              Refresh Page
            </Button>
            <Button variant="outline-secondary" onClick={() => (window.location.href = '/dashboard')}>
              <i className="bi bi-house me-2" />
              Go to Dashboard
            </Button>
          </div>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <Alert variant="danger" className="mt-4 text-start">
              <Alert.Heading>Error Details (Development Only)</Alert.Heading>
              <p className="mb-2">
                <strong>Message:</strong> {this.state.error.toString()}
              </p>
              {this.state.errorInfo && (
                <details className="mt-3">
                  <summary style={{ cursor: 'pointer' }}>Stack Trace</summary>
                  <pre className="mt-2 small" style={{ whiteSpace: 'pre-wrap' }}>
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}
            </Alert>
          )}
        </div>
      </Container>
    );
  }

  renderRouteLevelError() {
    return (
      <Container className="mt-4">
        <Alert variant="danger">
          <Alert.Heading>
            <i className="bi bi-exclamation-triangle me-2" />
            Unable to Load Page
          </Alert.Heading>
          <p className="mb-3">
            An error occurred while loading this page. Please try again or go back to the previous page.
          </p>
          <div className="d-flex gap-2">
            <Button variant="danger" size="sm" onClick={this.handleReset}>
              <i className="bi bi-arrow-clockwise me-2" />
              Try Again
            </Button>
            <Button variant="outline-secondary" size="sm" onClick={() => window.history.back()}>
              <i className="bi bi-arrow-left me-2" />
              Go Back
            </Button>
          </div>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <details className="mt-3">
              <summary style={{ cursor: 'pointer' }}>Error Details (Development Only)</summary>
              <pre className="mt-2 small" style={{ whiteSpace: 'pre-wrap' }}>
                {this.state.error.toString()}
              </pre>
            </details>
          )}
        </Alert>
      </Container>
    );
  }

  renderWidgetLevelError() {
    return (
      <Alert variant="warning" className="mb-3">
        <div className="d-flex align-items-center justify-content-between">
          <div>
            <i className="bi bi-exclamation-circle me-2" />
            <strong>Unable to load this section</strong>
            {this.props.widgetName && <span className="ms-1">({this.props.widgetName})</span>}
          </div>
          <Button variant="outline-warning" size="sm" onClick={this.handleReset}>
            <i className="bi bi-arrow-clockwise me-1" />
            Retry
          </Button>
        </div>
        {process.env.NODE_ENV === 'development' && this.state.error && (
          <details className="mt-2">
            <summary className="small" style={{ cursor: 'pointer' }}>Error Details</summary>
            <pre className="mt-2 small mb-0" style={{ whiteSpace: 'pre-wrap' }}>
              {this.state.error.toString()}
            </pre>
          </details>
        )}
      </Alert>
    );
  }

  renderCustomFallback() {
    const { fallback } = this.props;
    if (typeof fallback === 'function') {
      return fallback(this.state.error, this.handleReset);
    }
    return fallback;
  }

  render() {
    if (this.state.hasError) {
      // Custom fallback provided
      if (this.props.fallback) {
        return this.renderCustomFallback();
      }

      // Render based on level
      switch (this.props.level) {
        case 'app':
          return this.renderAppLevelError();
        case 'route':
          return this.renderRouteLevelError();
        case 'widget':
          return this.renderWidgetLevelError();
        default:
          return this.renderRouteLevelError();
      }
    }

    return this.props.children;
  }
}

ErrorBoundary.defaultProps = {
  level: 'route',
  fallback: null,
  onError: null,
  onReset: null,
  widgetName: null,
};

export default ErrorBoundary;
