import { useState } from 'react';
import { Link } from 'react-router-dom';
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

const Overlay = styled.div`
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
`;

const Modal = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.borderRadius.xl};
  padding: ${({ theme }) => theme.spacing.xxl};
  max-width: 400px;
  width: 90%;
  text-align: center;
  box-shadow: ${({ theme }) => theme.shadow.lg};
`;

const ModalTitle = styled.h2`
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: ${({ theme }) => theme.spacing.sm};
`;

const ModalText = styled.p`
  color: ${({ theme }) => theme.colors.textLight};
  margin-bottom: ${({ theme }) => theme.spacing.xl};
`;

const CloseButton = styled.button`
  padding: ${({ theme }) => `${theme.spacing.sm} ${theme.spacing.xl}`};
  background: ${({ theme }) => theme.colors.primary};
  color: #fff;
  font-weight: 600;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  transition: background 0.2s;

  &:hover {
    background: ${({ theme }) => theme.colors.primaryHover};
  }
`;

export default function Cart() {
  const { cartItems, cartTotal } = useCart();
  const [showModal, setShowModal] = useState(false);

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
        <PayButton onClick={() => setShowModal(true)}>Pay Now</PayButton>
        <ShopLink to="/">Continue Shopping &rarr;</ShopLink>
      </Summary>

      {showModal && (
        <Overlay onClick={() => setShowModal(false)}>
          <Modal onClick={(e) => e.stopPropagation()}>
            <ModalTitle>Payment Coming Soon</ModalTitle>
            <ModalText>
              This is a demo store. Payment processing will be available in a
              future update!
            </ModalText>
            <CloseButton onClick={() => setShowModal(false)}>Got it</CloseButton>
          </Modal>
        </Overlay>
      )}
    </Wrapper>
  );
}
