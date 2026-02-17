import styled from 'styled-components';

const FooterWrapper = styled.footer`
  margin-top: auto;
  padding: ${({ theme }) => `${theme.spacing.xl} ${theme.spacing.xl}`};
  text-align: center;
  color: ${({ theme }) => theme.colors.textMuted};
  font-size: 0.85rem;
  border-top: 1px solid ${({ theme }) => theme.colors.border};
`;

export default function Footer() {
  return (
    <FooterWrapper>
      &copy; {new Date().getFullYear()} SimpleShop. All rights reserved.
    </FooterWrapper>
  );
}
