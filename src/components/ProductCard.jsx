import styled from 'styled-components';
import { useCart } from '../context/CartContext';
import { sendMetaEvent } from '../lib/metaEvent';

const Card = styled.div`
  background: ${({ theme }) => theme.colors.surface};
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  overflow: hidden;
  box-shadow: ${({ theme }) => theme.shadow.md};
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;

  &:hover {
    transform: translateY(-4px);
    box-shadow: ${({ theme }) => theme.shadow.lg};
  }
`;

const ImageWrapper = styled.div`
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: ${({ theme }) => theme.colors.border};
`;

const Img = styled.img`
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s;

  ${Card}:hover & {
    transform: scale(1.05);
  }
`;

const Body = styled.div`
  padding: ${({ theme }) => theme.spacing.lg};
  display: flex;
  flex-direction: column;
  flex: 1;
`;

const Name = styled.h3`
  font-size: 1.1rem;
  font-weight: 600;
  margin-bottom: ${({ theme }) => theme.spacing.xs};
`;

const Description = styled.p`
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.textLight};
  margin-bottom: ${({ theme }) => theme.spacing.md};
  flex: 1;
`;

const Bottom = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Price = styled.span`
  font-size: 1.25rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text};
`;

const AddButton = styled.button`
  padding: ${({ theme }) => `${theme.spacing.sm} ${theme.spacing.lg}`};
  background: ${({ theme }) => theme.colors.primary};
  color: #fff;
  font-weight: 600;
  font-size: 0.875rem;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  transition: background 0.2s;

  &:hover {
    background: ${({ theme }) => theme.colors.primaryHover};
  }
`;

export default function ProductCard({ product }) {
  const { addToCart } = useCart();

  const handleAddToCart = () => {
    addToCart(product);
    sendMetaEvent({
      eventName: 'AddToCart',
      customData: {
        content_type: 'product',
        content_ids: [String(product.id)],
        currency: 'USD',
        value: product.price,
      },
    });
  };

  return (
    <Card>
      <ImageWrapper>
        <Img src={product.image} alt={product.name} loading="lazy" />
      </ImageWrapper>
      <Body>
        <Name>{product.name}</Name>
        <Description>{product.description}</Description>
        <Bottom>
          <Price>${product.price.toFixed(2)}</Price>
          <AddButton onClick={handleAddToCart}>&#9650; Add to Cart</AddButton>
        </Bottom>
      </Body>
    </Card>
  );
}
