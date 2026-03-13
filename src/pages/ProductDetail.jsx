import { useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import styled from 'styled-components';
import products from '../data/products';
import { useCart } from '../context/CartContext';
import { sendEvent } from '../lib/trackEvent';

const Wrapper = styled.div`
  max-width: 1000px;
  margin: 0 auto;
  padding: ${({ theme }) => theme.spacing.xl};
`;

const BackLink = styled(Link)`
  display: inline-flex;
  align-items: center;
  gap: ${({ theme }) => theme.spacing.xs};
  color: ${({ theme }) => theme.colors.textLight};
  font-size: 0.875rem;
  margin-bottom: ${({ theme }) => theme.spacing.xl};
  text-decoration: none;
  transition: color 0.2s;

  &:hover {
    color: ${({ theme }) => theme.colors.primary};
  }
`;

const ProductGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  gap: ${({ theme }) => theme.spacing.xl};

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    grid-template-columns: 1fr 1fr;
  }
`;

const ImageContainer = styled.div`
  border-radius: ${({ theme }) => theme.borderRadius.lg};
  overflow: hidden;
  background: ${({ theme }) => theme.colors.border};
`;

const Img = styled.img`
  width: 100%;
  display: block;
  object-fit: cover;
`;

const Info = styled.div`
  display: flex;
  flex-direction: column;
  gap: ${({ theme }) => theme.spacing.md};
`;

const Category = styled.span`
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: ${({ theme }) => theme.colors.primary};
`;

const Name = styled.h1`
  font-size: 2rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text};
  margin: 0;
`;

const Brand = styled.span`
  font-size: 0.875rem;
  color: ${({ theme }) => theme.colors.textLight};
`;

const Price = styled.span`
  font-size: 1.75rem;
  font-weight: 700;
  color: ${({ theme }) => theme.colors.text};
`;

const Description = styled.p`
  font-size: 1rem;
  line-height: 1.6;
  color: ${({ theme }) => theme.colors.textLight};
`;

const AddButton = styled.button`
  padding: ${({ theme }) => `${theme.spacing.md} ${theme.spacing.xl}`};
  background: ${({ theme }) => theme.colors.primary};
  color: #fff;
  font-weight: 600;
  font-size: 1rem;
  border-radius: ${({ theme }) => theme.borderRadius.md};
  transition: background 0.2s;
  align-self: flex-start;

  &:hover {
    background: ${({ theme }) => theme.colors.primaryHover};
  }
`;

const NotFound = styled.div`
  text-align: center;
  padding: ${({ theme }) => theme.spacing.xxl};
  color: ${({ theme }) => theme.colors.textLight};
`;

export default function ProductDetail() {
  const { id } = useParams();
  const { addToCart } = useCart();

  const product = products.find((p) => String(p.id) === id);

  useEffect(() => {
    if (!product) return;
    sendEvent({
      eventName: 'ViewContent',
      customData: {
        content_type: 'product',
        content_ids: [String(product.id)],
        content_names: [product.name],
        currency: 'USD',
        value: product.price,
      },
    });
  }, [product]);

  if (!product) {
    return (
      <Wrapper>
        <NotFound>
          <h2>Product not found</h2>
          <BackLink to="/">&#8592; Back to Shop</BackLink>
        </NotFound>
      </Wrapper>
    );
  }

  const handleAddToCart = () => {
    addToCart(product);
    sendEvent({
      eventName: 'AddToCart',
      customData: {
        content_type: 'product',
        content_ids: [String(product.id)],
        content_names: [product.name],
        currency: 'USD',
        value: product.price,
      },
    });
  };

  return (
    <Wrapper>
      <BackLink to="/">&#8592; Back to Shop</BackLink>
      <ProductGrid>
        <ImageContainer>
          <Img src={product.image} alt={product.name} />
        </ImageContainer>
        <Info>
          <Category>{product.category}</Category>
          <Name>{product.name}</Name>
          <Brand>by {product.brand}</Brand>
          <Price>${product.price.toFixed(2)}</Price>
          <Description>{product.description}</Description>
          <AddButton onClick={handleAddToCart}>&#9650; Add to Cart</AddButton>
        </Info>
      </ProductGrid>
    </Wrapper>
  );
}
