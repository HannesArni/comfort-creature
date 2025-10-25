/**
 * Color palette for Comfort Creature frontend
 * Design prioritizes clarity, accessibility, and technical visualization
 */

export const colors = {
  // Background & Base
  BACKGROUND: '#ffffff', // Clean white
  SURFACE: '#f6f8fa', // Subtle gray surface
  TEXT_PRIMARY: '#1f2328', // Dark gray text
  TEXT_SECONDARY: '#636c76', // Medium gray

  // Semantic Colors - Robot Navigation
  ROBOT: '#0969da', // Bold blue - high visibility main actor
  TARGET: '#1a7f37', // Rich green - clear goal indicator
  OBSTACLE: '#cf222e', // Bold red - immediate danger recognition
  PATH: '#8250df', // Purple - distinct from robot and target
  SENSOR_RANGE: '#bf8700', // Deep orange - sensor activity (use with opacity)

  // Status Colors
  SUCCESS: '#1a7f37', // Rich green - unmistakable success
  WARNING: '#bf8700', // Deep orange - attention needed
  ERROR: '#cf222e', // Bold red - critical alert
  INFO: '#0969da', // Blue - informational

  // UI Controls
  BUTTON_PRIMARY: '#1f883d', // Green button
  BUTTON_PRIMARY_HOVER: '#1a7f37', // Darker green on hover
  BUTTON_SECONDARY: '#e7e9eb', // Light gray
  BUTTON_SECONDARY_HOVER: '#d1d4d8', // Darker gray on hover
  BORDER: '#d1d9e0', // Clear borders

  // Grid & Canvas
  GRID_MINOR: '#eaeef2', // Subtle light grid
  GRID_MAJOR: '#eaeef2', // More visible major grid lines
  GRID_ORIGIN: '#636c76', // Origin crosshair
  GRID_LABEL: '#636c76', // Grid coordinate labels
} as const
