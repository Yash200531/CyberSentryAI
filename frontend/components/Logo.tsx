import React, { CSSProperties } from 'react';
import { ShieldAlert } from 'lucide-react';

type LogoSize = 'small' | 'medium' | 'large';

type LogoProps = {
  size?: LogoSize;
  showText?: boolean;
  text?: string;
  className?: string;
};

const sizeMap: Record<LogoSize, { icon: number; font: number; gap: number }> = {
  small: { icon: 24, font: 14, gap: 8 },
  medium: { icon: 32, font: 16, gap: 8 },
  large: { icon: 40, font: 20, gap: 12 },
};

const Logo: React.FC<LogoProps> = ({
  size = 'medium',
  showText = true,
  text = 'CYBERSENTRY',
  className = '',
}) => {
  const { icon, font, gap } = sizeMap[size];
  const style = {
    ['--logo-size' as string]: `${icon}px`,
    ['--logo-font' as string]: `${font}px`,
    ['--logo-gap' as string]: `${gap}px`,
  } as CSSProperties;

  return (
    <div
      className={`inline-flex items-center gap-[var(--logo-gap)] select-none ${className}`}
      style={style}
    >
      <ShieldAlert
        className="w-[var(--logo-size)] h-[var(--logo-size)] text-cyber-primary"
        strokeWidth={1.75}
      />
      {showText && (
        <span className="font-display font-semibold tracking-[0.2em] text-white leading-none text-[var(--logo-font)]">
          {text.includes('SENTRY') ? (
            <>
              {text.split('SENTRY')[0]}SENTRY
              {text.split('SENTRY')[1] ? (
                <span className="text-cyber-primary">{text.split('SENTRY')[1]}</span>
              ) : null}
            </>
          ) : (
            <>{text}</>
          )}
        </span>
      )}
    </div>
  );
};

export default Logo;
