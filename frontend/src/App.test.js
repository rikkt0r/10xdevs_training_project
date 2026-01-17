import { render, screen } from '@testing-library/react';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import { store } from './store';

test('renders app title', () => {
  render(
    <Provider store={store}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </Provider>
  );
  const titleElement = screen.getByText(/Simple Issue Tracker/i);
  expect(titleElement).toBeInTheDocument();
});
