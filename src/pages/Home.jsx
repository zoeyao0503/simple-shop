import { useEffect } from 'react';
import styled from 'styled-components';
import ProductCard from '../components/ProductCard';
import LeadForm from '../components/LeadForm';
import products from '../data/products';
import { sendMetaEvent } from '../lib/metaEvent';

const Hero = styled.section`
  text-align: center;
  padding: ${({ theme }) => `${theme.spacing.xxl} ${theme.spacing.xl}`};
  background: linear-gradient(135deg, #FF4500 0%, #FF6634 100%);
  color: #fff;
`;

const HeroSnoo = styled.div`
  font-size: 3.5rem;
  margin-bottom: ${({ theme }) => theme.spacing.md};
  line-height: 1;
`;

const HeroTitle = styled.h1`
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: ${({ theme }) => theme.spacing.sm};
  color: #fff;

  @media (min-width: ${({ theme }) => theme.breakpoints.md}) {
    font-size: 3rem;
  }
`;

const HeroSub = styled.p`
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  max-width: 560px;
  margin: 0 auto;
`;

const SectionTitle = styled.h2`
  font-size: 1.5rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: ${({ theme }) => theme.spacing.xl};
  color: ${({ theme }) => theme.colors.text};
`;

const UpvoteIcon = styled.span`
  color: ${({ theme }) => theme.colors.primary};
  margin-right: ${({ theme }) => theme.spacing.xs};
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
  useEffect(() => {
    sendMetaEvent({
      eventName: 'ViewContent',
      customData: {
        content_type: 'product',
        content_ids: products.map((p) => String(p.id)),
      },
    });
  }, []);

  return (
    <>
      <Hero>
        <HeroSnoo>
          <svg width="64" height="64" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
            <circle cx="10" cy="10" r="10" fill="#fff"/>
            <circle cx="10" cy="10.8" r="6.5" fill="#FF4500"/>
            <circle cx="7.2" cy="9.8" r="1.2" fill="#fff"/>
            <circle cx="12.8" cy="9.8" r="1.2" fill="#fff"/>
            <ellipse cx="10" cy="5" rx="1.8" ry="1.6" fill="#fff"/>
            <line x1="11.5" y1="4" x2="14" y2="2" stroke="#fff" strokeWidth="1.2" strokeLinecap="round"/>
            <circle cx="14.2" cy="2" r="1" fill="#fff"/>
            <path d="M7 12.5c0 0 1.2 1.5 3 1.5s3-1.5 3-1.5" fill="none" stroke="#fff" strokeWidth="0.8" strokeLinecap="round"/>
          </svg>
        </HeroSnoo>
        <HeroTitle>Welcome to SnooCommerce</HeroTitle>
        <HeroSub>
          Upvote-worthy finds for everyday life. Browse our collection and discover
          something awesome.
        </HeroSub>
      </Hero>

      <div style={{ paddingTop: '2rem' }}>
        <SectionTitle><UpvoteIcon>&#9650;</UpvoteIcon> Trending Products</SectionTitle>
      </div>
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
