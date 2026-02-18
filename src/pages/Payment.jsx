import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { useCart } from '../context/CartContext';
import { getRandomUser } from '../data/fakeUsers';
import { sendMetaEvent } from '../lib/metaEvent';

const Wrapper = styled.div`
  max-width: 860px;
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

const Grid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: ${({ theme }) => theme.spacing.xl};

  @media (max-width: ${({ theme }) => theme.breakpoints.md}) {
    grid-template-columns: 1fr;
  }
`;

const Section = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.borderRadius.xl};
  padding: ${({ theme }) => theme.spacing.xl};
  box-shadow: ${({ theme }) => theme.shadow.md};
`;

const SectionTitle = styled.h2`
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: ${({ theme }) => theme.spacing.lg};
  padding-bottom: ${({ theme }) => theme.spacing.sm};
  border-bottom: 2px solid ${({ theme }) => theme.colors.border};
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.md};
`;

const FieldGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.xs};
`;

const Label = styled.label`
  font-size: 0.85rem;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.textLight};
`;

const Input = styled.input`
  padding: ${({ theme }) => `${theme.spacing.sm} ${theme.spacing.md}`};
  border: 1px solid ${({ theme }) => theme.colors.border};
  border-radius: ${({ theme }) => theme.borderRadius.md};
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
  }
`;

const OrderItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: ${({ theme }) => theme.spacing.sm} 0;
  font-size: 0.95rem;

  &:not(:last-child) {
    border-bottom: 1px solid ${({ theme }) => theme.colors.border};
  }
`;

const ItemName = styled.span`
  color: ${({ theme }) => theme.colors.text};
`;

const ItemQty = styled.span`
  color: ${({ theme }) => theme.colors.textLight};
  font-size: 0.85rem;
`;

const ItemPrice = styled.span`
  font-weight: 600;
  white-space: nowrap;
`;

const TotalRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: ${({ theme }) => theme.spacing.md};
  padding-top: ${({ theme }) => theme.spacing.md};
  border-top: 2px solid ${({ theme }) => theme.colors.text};
  font-size: 1.2rem;
  font-weight: 700;
`;

const PayButton = styled.button`
  width: 100%;
  padding: ${({ theme }) => `${theme.spacing.md} ${theme.spacing.xl}`};
  background: ${({ theme }) => theme.colors.primary};
  color: #fff;
  font-weight: 700;
  font-size: 1.1rem;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  margin-top: ${({ theme }) => theme.spacing.lg};
  transition: background 0.2s;

  &:hover {
    background: ${({ theme }) => theme.colors.primaryHover};
  }
`;

const BackLink = styled(Link)`
  display: inline-block;
  margin-top: ${({ theme }) => theme.spacing.lg};
  color: ${({ theme }) => theme.colors.primary};
  font-weight: 600;
  font-size: 0.95rem;
  transition: opacity 0.2s;

  &:hover {
    opacity: 0.8;
  }
`;

export default function Payment() {
  const { cartItems, cartTotal } = useCart();
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [address, setAddress] = useState('');

  useEffect(() => {
    const user = getRandomUser();
    setName(user.name);
    setEmail(user.email);
    setPhone(user.phone);
    setAddress(user.address);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMetaEvent({
      eventName: 'Purchase',
      customData: {
        content_type: 'product',
        content_ids: cartItems.map((item) => String(item.id)),
        currency: 'USD',
        value: cartTotal,
      },
    });
    navigate('/payment/success', { state: { name, email } });
  };

  if (cartItems.length === 0) {
    return (
      <Wrapper>
        <Title>Payment</Title>
        <p>Your cart is empty.</p>
        <BackLink to="/">&larr; Continue Shopping</BackLink>
      </Wrapper>
    );
  }

  return (
    <Wrapper>
      <Title>Complete Payment</Title>
      <Form onSubmit={handleSubmit}>
        <Grid>
          <Section>
            <SectionTitle>Contact Information</SectionTitle>
            <FieldGroup>
              <Label htmlFor="name">Full Name</Label>
              <Input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </FieldGroup>
            <FieldGroup style={{ marginTop: '1rem' }}>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </FieldGroup>
            <FieldGroup style={{ marginTop: '1rem' }}>
              <Label htmlFor="phone">Phone Number</Label>
              <Input
                id="phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
              />
            </FieldGroup>
            <FieldGroup style={{ marginTop: '1rem' }}>
              <Label htmlFor="address">Shipping Address</Label>
              <Input
                id="address"
                type="text"
                value={address}
                onChange={(e) => setAddress(e.target.value)}
                required
              />
            </FieldGroup>
          </Section>

          <div>
            <Section>
              <SectionTitle>Order Summary</SectionTitle>
              {cartItems.map((item) => (
                <OrderItem key={item.id}>
                  <div>
                    <ItemName>{item.name}</ItemName>
                    <ItemQty> &times; {item.qty}</ItemQty>
                  </div>
                  <ItemPrice>${(item.price * item.qty).toFixed(2)}</ItemPrice>
                </OrderItem>
              ))}
              <TotalRow>
                <span>Total</span>
                <span>${cartTotal.toFixed(2)}</span>
              </TotalRow>
              <PayButton type="submit">Complete Payment</PayButton>
            </Section>
            <BackLink to="/cart">&larr; Back to Cart</BackLink>
          </div>
        </Grid>
      </Form>
    </Wrapper>
  );
}
