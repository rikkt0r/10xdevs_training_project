import React from 'react';
import { Placeholder } from 'react-bootstrap';
import './Skeleton.css';

/**
 * Base Skeleton component for loading states
 * Uses Bootstrap's Placeholder component with custom styling
 */
const Skeleton = ({
  width = '100%',
  height = '1rem',
  variant = 'default',
  animation = 'wave',
  className = '',
  style = {},
}) => {
  return (
    <Placeholder
      animation={animation}
      className={`skeleton skeleton-${variant} ${className}`}
      style={{
        width,
        height,
        display: 'inline-block',
        ...style,
      }}
    />
  );
};

/**
 * SkeletonText component for text loading
 */
export const SkeletonText = ({ lines = 3, className = '' }) => {
  return (
    <div className={className}>
      {Array.from({ length: lines }).map((_, index) => (
        <Skeleton
          key={index}
          width={index === lines - 1 ? '70%' : '100%'}
          height="1rem"
          className="mb-2"
        />
      ))}
    </div>
  );
};

/**
 * SkeletonCard component for card loading
 */
export const SkeletonCard = ({ className = '' }) => {
  return (
    <div className={`card ${className}`}>
      <div className="card-body">
        <Skeleton width="60%" height="1.5rem" className="mb-3" />
        <SkeletonText lines={3} />
      </div>
    </div>
  );
};

/**
 * SkeletonTable component for table loading
 */
export const SkeletonTable = ({ rows = 5, columns = 4, className = '' }) => {
  return (
    <div className={`table-responsive ${className}`}>
      <table className="table">
        <thead>
          <tr>
            {Array.from({ length: columns }).map((_, colIndex) => (
              <th key={colIndex}>
                <Skeleton width="80%" height="1rem" />
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: columns }).map((_, colIndex) => (
                <td key={colIndex}>
                  <Skeleton width="90%" height="1rem" />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

/**
 * SkeletonList component for list loading
 */
export const SkeletonList = ({ items = 5, className = '' }) => {
  return (
    <div className={className}>
      {Array.from({ length: items }).map((_, index) => (
        <div key={index} className="d-flex align-items-center mb-3">
          <Skeleton width="3rem" height="3rem" className="rounded me-3" variant="circle" />
          <div className="flex-grow-1">
            <Skeleton width="40%" height="1rem" className="mb-2" />
            <Skeleton width="80%" height="0.875rem" />
          </div>
        </div>
      ))}
    </div>
  );
};

/**
 * SkeletonForm component for form loading
 */
export const SkeletonForm = ({ fields = 3, className = '' }) => {
  return (
    <div className={className}>
      {Array.from({ length: fields }).map((_, index) => (
        <div key={index} className="mb-3">
          <Skeleton width="30%" height="1rem" className="mb-2" />
          <Skeleton width="100%" height="2.5rem" />
        </div>
      ))}
      <Skeleton width="8rem" height="2.5rem" className="mt-3" />
    </div>
  );
};

export default Skeleton;
