/**
 * Utility function to merge classNames
 * Simple implementation without external dependencies
 */
export function cn(...classes) {
  return classes.filter(Boolean).join(' ');
}
