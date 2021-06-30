import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './styles.module.css';
import Translate, {translate} from '@docusaurus/Translate';
import { preferences } from 'service-worker-i18n-redirect/preferences';
window.addEventListener('DOMContentLoaded', async () => {
  const language = await preferences.get('lang');
  if (language === undefined) {
    preferences.set('lang', lang.value); // Language determined from localization user landed on
  }
});

const features = [
  {
    title: 'Powered by Python',
    imageUrl: 'img/python-logo.svg',
    description: (
      <>
        The App is Written in Python Version 3.7 .
      </>
    ),
  },
];

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  return (
    <header className={clsx('hero hero--primary', styles.heroBanner)}>
      <div className="container">
        <h1 className="hero__title">{siteConfig.title}</h1>
        <p className="hero__subtitle">{siteConfig.tagline}</p>
        <div className={styles.buttons}>
          <Link
            className="button button--secondary button--lg"
            to="/docs/intro">
            Docusaurus Tutorial - 5min ⏱️
          </Link>
        </div>
      </div>
    </header>
  );
}

function Home() {
  const context = useDocusaurusContext();
  const {siteConfig = {}} = context;
  return (
    <Layout
      title={`Alpha-Video`}
      description="Play YouTube On alexa">
      <header className={clsx('hero hero--primary', styles.heroBanner)}>
        <div className="container">
          <h1 className="hero__title"><Translate>
	    Alpha Video
	  </Translate></h1>
          <p className="hero__subtitle"><Translate>
		  Youtube on Alexa
		  </Translate></p>
          <div className={styles.buttons}>
            <Link
              className={clsx(
                'button button--outline button--secondary button--lg',
                styles.getStarted,
              )}
              to={useBaseUrl('docs/start')}>
              Get Started
            </Link>
          </div>
        </div>
      </header>
      <main>
  <div className={clsx('col col--4', styles.feature)}>
    <div className="text--center">
      <img className={styles.featureImage} src='img/python-logo.svg' alt="Python logo"/>
      <h3><Translate description="Powered by Python">Powered by Python</Translate>
      </h3>
      <p>
        <Translate>
          The App is Written in Python Version 3.7 .
        </Translate>
      </p>
    </div>
  </div>
</main>
    </Layout>
  );
}

export default Home;
