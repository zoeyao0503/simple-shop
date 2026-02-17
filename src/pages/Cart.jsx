import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useCart } from '../context/CartContext';
import CartItem from '../components/CartItem';

const Wrapper = styled.div`
  max-width: 800px;
  margin: 0 auto;
  padding: ${({ theme }) => `${theme.spacing.xxl} ${theme.spacing.xl}`};
  width: 100%;
  flex: 1;
`;

const Title = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: ${({ theme }) => theme.spacing.xl};
`;

const EmptyMsg = styled.div`
  text-align: center;
  padding: ${({ theme }) => theme.spacing.xxl} 0;
  color: ${({ theme }) => theme.colors.textLight};
`;

const ShopLink = styled(Link)`
  display: inline-block;
  margin-top: ${({ theme }) => theme.spacing.lg};
  color: ${({ theme }) => theme.colors.primary};
  font-weight: 600;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.8;
  }
`;

const Summary = styled.div`
  margin-top: ${({ theme }) => theme.spacing.xl};
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: ${({ theme }) => theme.spacing.md};
`;

const Total = styled.span`
  font-size: 1.25rem;
  font-weight: 700;
`;

const PayButton = styled.button`
  padding: ${({ theme }) => `${theme.spacing.md} ${theme.spacing.xxl}`};
  background: ${({ theme }) => theme.colors.primary};
  color: #fff;
  font-weight: 700;
  font-size: 1.1rem;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  transition: background 0.2s;

  &:hover {
    background: ${({ theme }) => theme.colors.primaryHover};
  }
`;


export default function Cart() {
  const { cartItems, cartTotal } = useCart();
  const navigate = useNavigate();

  if (cartItems.length === 0) {
    return (
      <Wrapper>
        <Title>Your Cart</Title>
        <EmptyMsg>
          <p>Your cart is empty.</p>
          <ShopLink to="/">Continue Shopping &rarr;</ShopLink>
        </EmptyMsg>
      </Wrapper>
    );
  }

  return (
    <Wrapper>
      <Title>Your Cart</Title>
      {cartItems.map((item) => (
        <CartItem key={item.id} item={item} />
      ))}
      <Summary>
        <Total>Total: ${cartTotal.toFixed(2)}</Total>
        <PayButton onClick={() => navigate('/payment')}>Pay Now</PayButton>
        <ShopLink to="/">Continue Shopping &rarr;</ShopLink>
      </Summary>

    </Wrapper>
  );
}
