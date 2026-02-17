import styled from 'styled-components';
import ProductCard from '../components/ProductCard';
import LeadForm from '../components/LeadForm';
import products from '../data/products';

const Hero = styled.section`
  text-align: center;
  padding: ${({ theme }) => `${theme.spacing.xxl} ${theme.spacing.xl}`};
`;

const HeroTitle = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: ${({ theme }) => theme.spacing.sm};
  color: ${({ theme }) => theme.colors.text};

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    font-size: 3rem;
  }
`;

const HeroSub = styled.p`
  font-size: 1.1rem;
  color: ${({ theme }) => theme.colors.textLight};
  max-width: 560px;
  margin: 0 auto;
`;

const SectionTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: ${({ theme }) => theme.spacing.xl};
`;

const Grid = styled.section`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: ${({ theme }) => theme.spacing.xl};
  padding: ${({ theme }) => `0 ${theme.spacing.xl} ${theme.spacing.xxl}`};
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
`;

const LeadSection = styled.section`
  padding: ${({ theme }) => `${theme.spacing.xxl} ${theme.spacing.xl}`};
  background: ${({ theme }) => theme.colors.background};
`;

export default function Home() {
  return (
    <>
      <Hero>
        <HeroTitle>Discover Quality Products</HeroTitle>
        <HeroSub>
          Handpicked essentials for everyday life. Browse our collection and find
          something you love.
        </HeroSub>
      </Hero>

      <SectionTitle>Our Products</SectionTitle>
      <Grid>
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </Grid>

      <LeadSection>
        <LeadForm />
      </LeadSection>
    </>
  );
}
