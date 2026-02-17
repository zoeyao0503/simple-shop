import { Link, useLocation, Navigate } from 'react-router-dom';
import styled from 'styled-components';

const Wrapper = styled.div`
  max-width: 520px;
  margin: 0 auto;
  padding: ${({ theme }) => `${theme.spacing.xxl} ${theme.spacing.xl}`};
  width: 100%;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
`;

const SuccessIcon = styled.div`
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: ${({ theme }) => theme.colors.successBg};
  color: ${({ theme }) => theme.colors.success};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  margin-bottom: ${({ theme }) => theme.spacing.xl};
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: ${({ theme }) => theme.spacing.md};
`;

const Message = styled.p`
  color: ${({ theme }) => theme.colors.textLight};
  font-size: 1.05rem;
  line-height: 1.6;
  margin-bottom: ${({ theme }) => theme.spacing.xxl};
`;

const ShopButton = styled(Link)`
  display: inline-block;
  padding: ${({ theme }) => `${theme.spacing.md} ${theme.spacing.xxl}`};
  background: ${({ theme }) => theme.colors.primary};
  color: #fff;
  font-weight: 700;
  font-size: 1.1rem;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  text-decoration: none;
  transition: background 0.2s;

  &:hover {
    background: ${({ theme }) => theme.colors.primaryHover};
  }
`;

export default function PaymentSuccess() {
  const location = useLocation();
  const { name, email } = location.state || {};

  if (!name) {
    return <Navigate to="/" replace />;
  }

  return (
    <Wrapper>
      <SuccessIcon>&#10003;</SuccessIcon>
      <Title>Payment Successful!</Title>
      <Message>
        Thank you, {name}! Your order has been placed successfully.
        A confirmation will be sent to {email}.
      </Message>
      <ShopButton to="/">Back to Shop</ShopButton>
    </Wrapper>
  );
}
