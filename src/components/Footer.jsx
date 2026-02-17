import styled from 'styled-components';

const FooterWrapper = styled.footer`
  margin-top: auto;
  padding: ${({ theme }) => `${theme.spacing.xl} ${theme.spacing.xl}`};
  text-align: center;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.85rem;
  border-top: 2px solid ${({ theme }) => theme.colors.primary};
  background: ${({ theme }) => theme.colors.surface};
`;

const SnooFooterIcon = styled.span`
  display: inline-block;
  margin-right: 0.3rem;
  vertical-align: middle;
`;

export default function Footer() {
  return (
    <FooterWrapper>
      <SnooFooterIcon>
        <svg width="16" height="16" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
          <circle cx="10" cy="10" r="10" fill="#FF4500"/>
          <circle cx="10" cy="10.8" r="6.5" fill="#fff"/>
          <circle cx="7.2" cy="9.8" r="1.2" fill="#FF4500"/>
          <circle cx="12.8" cy="9.8" r="1.2" fill="#FF4500"/>
          <ellipse cx="10" cy="5" rx="1.8" ry="1.6" fill="#FF4500"/>
          <line x1="11.5" y1="4" x2="14" y2="2" stroke="#FF4500" strokeWidth="1.2" strokeLinecap="round"/>
          <circle cx="14.2" cy="2" r="1" fill="#FF4500"/>
          <path d="M7 12.5c0 0 1.2 1.5 3 1.5s3-1.5 3-1.5" fill="none" stroke="#FF4500" strokeWidth="0.8" strokeLinecap="round"/>
        </svg>
      </SnooFooterIcon>
      &copy; {new Date().getFullYear()} SnooCommerce. All rights reserved.
    </FooterWrapper>
  );
}
