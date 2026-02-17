import styled from 'styled-components';
import { useCart } from '../context/CartContext';

const Row = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.lg};
  padding: ${({ theme }) => theme.spacing.lg} 0;
  border-bottom: 1px solid ${({ theme }) => theme.colors.border};

  @media (max-width: ${({ theme }) => theme.breakpoints.sm}) {
    flex-direction: column;
    align-items: flex-start;
  }
`;

const Img = styled.img`
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  flex-shrink: 0;
`;

const Info = styled.div`
  flex: 1;
`;

const Name = styled.h4`
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: ${({ theme }) => theme.spacing.xs};
`;

const Price = styled.span`
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.textLight};
`;

const Controls = styled.div`
  display: flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.sm};
`;

const QtyButton = styled.button`
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: ${({ theme }) => theme.colors.background};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.borderRadius.sm};
  font-size: 1rem;
  font-weight: 600;
  transition: background 0.15s;

  &:hover {
    background: ${({ theme }) => theme.colors.border};
  }
`;

const Qty = styled.span`
  min-width: 24px;
  text-align: center;
  font-weight: 600;
`;

const Subtotal = styled.span`
  font-weight: 700;
  font-size: 1rem;
  min-width: 80px;
  text-align: right;
`;

const RemoveButton = styled.button`
  background: none;
  color: ${({ theme }) => theme.colors.danger};
  font-size: 0.8rem;
  font-weight: 500;
  padding: ${({ theme }) => theme.spacing.xs};
  transition: color 0.15s;

  &:hover {
    color: ${({ theme }) => theme.colors.dangerHover};
  }
`;

export default function CartItem({ item }) {
  const { updateQuantity, removeFromCart } = useCart();

  return (
    <Row>
      <Img src={item.image} alt={item.name} />
      <Info>
        <Name>{item.name}</Name>
        <Price>${item.price.toFixed(2)} each</Price>
      </Info>
      <Controls>
        <QtyButton onClick={() => updateQuantity(item.id, item.qty - 1)}>-</QtyButton>
        <Qty>{item.qty}</Qty>
        <QtyButton onClick={() => updateQuantity(item.id, item.qty + 1)}>+</QtyButton>
      </Controls>
      <Subtotal>${(item.price * item.qty).toFixed(2)}</Subtotal>
      <RemoveButton onClick={() => removeFromCart(item.id)}>Remove</RemoveButton>
    </Row>
  );
}
