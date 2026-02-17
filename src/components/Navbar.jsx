import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { useCart } from '../context/CartContext';

const Nav = styled.nav`
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${({ theme }) => `${theme.spacing.md} ${theme.spacing.xl}`};
  background: ${({ theme }) => theme.colors.surface};
  border-bottom: 2px solid ${({ theme }) => theme.colors.primary};
  box-shadow: ${({ theme }) => theme.shadow.sm};

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    padding: ${({ theme }) => `${theme.spacing.md} ${theme.spacing.xxl}`};
  }
`;

const LogoLink = styled(Link)`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
`;

const SnooIcon = styled.span`
  font-size: 2rem;
  line-height: 1;
`;

const LogoText = styled.span`
  font-size: 1.4rem;
  font-weight: 700;
  letter-spacing: -0.5px;

  .snoo {
    color: ${({ theme }) => theme.colors.primary};
  }
  .commerce {
    color: ${({ theme }) => theme.colors.text};
  }
`;

const CartLink = styled(Link)`
  position: relative;
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.xs};
  font-weight: 500;
  color: ${({ theme }) => theme.colors.text};
  transition: color 0.2s;

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const CartIcon = styled.span`
  font-size: 1.4rem;
`;

const Badge = styled.span`
  position: absolute;
  top: -8px;
  right: -12px;
  background: ${({ theme }) => theme.colors.primary};
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  width: 20px;
  height: 20px;
  border-radius: ${({ theme }) => theme.borderRadius.full};
  display: flex;
  align-items: center;
  justify-content: center;
`;

export default function Navbar() {
  const { cartCount } = useCart();

  return (
    <Nav>
      <LogoLink to="/">
        <SnooIcon>
          <svg width="32" height="32" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="10" fill="#FF4500"/>
            <circle cx="10" cy="10.8" r="6.5" fill="#fff"/>
            <circle cx="7.2" cy="9.8" r="1.2" fill="#FF4500"/>
            <circle cx="12.8" cy="9.8" r="1.2" fill="#FF4500"/>
            <ellipse cx="10" cy="5" rx="1.8" ry="1.6" fill="#FF4500"/>
            <line x1="11.5" y1="4" x2="14" y2="2" stroke="#FF4500" strokeWidth="1.2" strokeLinecap="round"/>
            <circle cx="14.2" cy="2" r="1" fill="#FF4500"/>
            <path d="M7 12.5c0 0 1.2 1.5 3 1.5s3-1.5 3-1.5" fill="none" stroke="#FF4500" strokeWidth="0.8" strokeLinecap="round"/>
          </svg>
        </SnooIcon>
        <LogoText>
          <span className="snoo">Snoo</span>
          <span className="commerce">Commerce</span>
        </LogoText>
      </LogoLink>
      <CartLink to="/cart">
        <CartIcon>🛒</CartIcon>
        {cartCount > 0 && <Badge>{cartCount}</Badge>}
      </CartLink>
    </Nav>
  );
}
