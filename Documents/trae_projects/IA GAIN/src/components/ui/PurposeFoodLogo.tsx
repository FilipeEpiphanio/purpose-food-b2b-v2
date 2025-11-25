import React from 'react';

interface PurposeFoodLogoProps {
  size?: 'small' | 'medium' | 'large';
  variant?: 'default' | 'header' | 'card' | 'light';
  className?: string;
}

const PurposeFoodLogo: React.FC<PurposeFoodLogoProps> = ({ 
  size = 'medium', 
  variant = 'default',
  className = '' 
}) => {
  const sizeClasses = {
    small: 'w-16 h-16',
    medium: 'w-24 h-24',
    large: 'w-32 h-32'
  };

  const variantClasses = {
    default: '',
    header: 'hover:scale-105 transition-transform duration-300',
    card: 'drop-shadow-lg',
    light: 'filter brightness-0 invert'
  };

  return (
    <div className={`${sizeClasses[size]} ${variantClasses[variant]} ${className}`}>
      <svg viewBox="0 0 200 200" className="w-full h-full">
        {/* Background circle with lace/doily border */}
        <defs>
          <pattern id="lacePattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
            <circle cx="10" cy="10" r="3" fill="#b98173" opacity="0.6" />
            <path d="M 5 10 Q 10 5 15 10 Q 10 15 5 10" fill="#c18a7b" opacity="0.4" />
          </pattern>
          
          <radialGradient id="backgroundGradient" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#f5dccb" />
            <stop offset="100%" stopColor="#f3d2c1" />
          </radialGradient>

          <linearGradient id="spoonGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#7a8590" />
            <stop offset="100%" stopColor="#6b7681" />
          </linearGradient>

          <linearGradient id="handleGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#d59b85" />
            <stop offset="100%" stopColor="#c58b75" />
          </linearGradient>
        </defs>

        {/* Outer decorative border */}
        <circle cx="100" cy="100" r="95" fill="url(#backgroundGradient)" stroke="#b98173" strokeWidth="2" />
        
        {/* Decorative lace pattern */}
        <circle cx="100" cy="100" r="90" fill="none" stroke="#c18a7b" strokeWidth="1" opacity="0.3" />
        
        {/* Inner cream circle */}
        <circle cx="100" cy="100" r="80" fill="#fef9f6" stroke="#e5b3a6" strokeWidth="1" opacity="0.8" />

        {/* Decorative hearts and flourishes */}
        <g transform="translate(100, 100)">
          {/* Left side decorative elements */}
          <g transform="translate(-45, -20)">
            <path d="M -5 -5 Q -10 -10 -5 -15 Q 0 -10 -5 -5" fill="#e5b3a6" opacity="0.6" transform="rotate(-20)" />
            <circle cx="-8" cy="-8" r="2" fill="#d59b85" opacity="0.7" />
            <path d="M -15 -5 Q -20 -8 -18 -12 Q -12 -15 -8 -12" stroke="#e5b3a6" strokeWidth="1.5" fill="none" opacity="0.5" />
          </g>

          {/* Right side decorative elements */}
          <g transform="translate(45, -20)">
            <path d="M 5 -5 Q 10 -10 5 -15 Q 0 -10 5 -5" fill="#e5b3a6" opacity="0.6" transform="rotate(20)" />
            <circle cx="8" cy="-8" r="2" fill="#d59b85" opacity="0.7" />
            <path d="M 15 -5 Q 20 -8 18 -12 Q 12 -15 8 -12" stroke="#e5b3a6" strokeWidth="1.5" fill="none" opacity="0.5" />
          </g>
        </g>

        {/* Spoon (left side) */}
        <g transform="translate(70, 60)">
          {/* Spoon bowl */}
          <ellipse cx="0" cy="0" rx="12" ry="15" fill="url(#spoonGradient)" stroke="#6b7681" strokeWidth="1" />
          <ellipse cx="0" cy="2" rx="8" ry="10" fill="#8a95a0" opacity="0.3" />
          
          {/* Spoon handle */}
          <rect x="-2" y="15" width="4" height="25" fill="url(#handleGradient)" rx="2" />
          <rect x="-1.5" y="15" width="3" height="25" fill="#d59b85" opacity="0.8" rx="1.5" />
          
          {/* Decorative accent on handle */}
          <circle cx="0" cy="25" r="3" fill="#e5b3a6" opacity="0.8" />
        </g>

        {/* Whisk (right side) */}
        <g transform="translate(130, 60)">
          {/* Whisk wires */}
          <g stroke="#7a8590" strokeWidth="2" fill="none" opacity="0.8">
            <ellipse rx="12" ry="8" transform="rotate(0)" />
            <ellipse rx="12" ry="8" transform="rotate(45)" />
            <ellipse rx="12" ry="8" transform="rotate(90)" />
            <ellipse rx="12" ry="8" transform="rotate(135)" />
          </g>
          
          {/* Whisk handle */}
          <rect x="-2" y="12" width="4" height="25" fill="url(#handleGradient)" rx="2" />
          <rect x="-1.5" y="12" width="3" height="25" fill="#d59b85" opacity="0.8" rx="1.5" />
          
          {/* Decorative accent on handle */}
          <circle cx="0" cy="22" r="3" fill="#e5b3a6" opacity="0.8" />
        </g>

        {/* Brand Text */}
        <g transform="translate(100, 110)">
          {/* PURPOUSE */}
          <text 
            x="0" 
            y="0" 
            textAnchor="middle" 
            className="fill-current text-[#8b5e50] font-serif font-bold"
            style={{ 
              fontSize: '18px', 
              letterSpacing: '3px',
              fontFamily: 'Georgia, serif'
            }}
          >
            PURPOUSE
          </text>
          
          {/* FOOD */}
          <text 
            x="0" 
            y="18" 
            textAnchor="middle" 
            className="fill-current text-[#8b5e50] font-serif font-semibold"
            style={{ 
              fontSize: '12px', 
              letterSpacing: '2px',
              fontFamily: 'Georgia, serif'
            }}
          >
            FOOD
          </text>
          
          {/* PRA ALEGRAR O CORAÇÃO */}
          <text 
            x="0" 
            y="38" 
            textAnchor="middle" 
            className="fill-current text-[#5c3f35] font-sans font-medium"
            style={{ 
              fontSize: '8px', 
              letterSpacing: '1px',
              fontFamily: 'Arial, sans-serif'
            }}
          >
            PRA ALEGRAR O CORAÇÃO
          </text>
        </g>

        {/* Additional decorative elements */}
        <g transform="translate(100, 100)">
          {/* Small dots around */}
          <circle cx="-60" cy="-10" r="1.5" fill="#e5b3a6" opacity="0.6" />
          <circle cx="60" cy="-10" r="1.5" fill="#e5b3a6" opacity="0.6" />
          <circle cx="-50" cy="40" r="1" fill="#d59b85" opacity="0.5" />
          <circle cx="50" cy="40" r="1" fill="#d59b85" opacity="0.5" />
          
          {/* Tiny flourishes */}
          <path d="M -70 0 Q -75 -5 -70 -10" stroke="#e5b3a6" strokeWidth="1" fill="none" opacity="0.4" />
          <path d="M 70 0 Q 75 -5 70 -10" stroke="#e5b3a6" strokeWidth="1" fill="none" opacity="0.4" />
        </g>
      </svg>
    </div>
  );
};

export default PurposeFoodLogo;