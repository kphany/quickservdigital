const qsTrackEvent = (eventName, metadata = {}) => {
  const payload = {
    event: eventName,
    page: window.location.pathname,
    timestamp: new Date().toISOString(),
    ...metadata,
  };

  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push(payload);

  if (window.gtag) {
    window.gtag('event', eventName, payload);
  }
};

const attachAnalyticsHooks = () => {
  document.querySelectorAll('a[href^="https://t.me/"] , a[href^="mailto:"] , .button, .contact-link, .nav-cta').forEach((link) => {
    link.addEventListener('click', () => {
      const label = link.textContent ? link.textContent.trim() : link.getAttribute('href');
      const href = link.getAttribute('href') || '';

      if (href.startsWith('mailto:')) {
        qsTrackEvent('email_click', { label, href });
      } else if (href.startsWith('https://t.me/')) {
        qsTrackEvent('telegram_click', { label, href });
      } else if (link.classList.contains('nav-cta') || link.classList.contains('button') || link.classList.contains('contact-link')) {
        qsTrackEvent('cta_click', { label, href });
      }
    }, { passive: true });
  });
};

const year = document.getElementById('year');
const sitePrefix = window.location.pathname.includes('/services/') ? '../' : '';

if (year) {
  year.textContent = new Date().getFullYear();
}

const nav = document.querySelector('.site-header nav');
const navWrap = document.querySelector('.nav-wrap');

if (nav && navWrap) {
  document.body.classList.add('nav-ready');
  nav.id = 'site-nav';

  const servicesMenu = nav.querySelector('.services-menu');
  if (servicesMenu) {
    const pricingLink = document.createElement('a');
    pricingLink.className = 'services-menu-pricing';
    pricingLink.href = `${sitePrefix}pricing.html`;
    pricingLink.textContent = 'Products & Pricing';
    servicesMenu.appendChild(pricingLink);
  }

  const navToggle = document.createElement('button');
  navToggle.className = 'nav-toggle';
  navToggle.type = 'button';
  navToggle.setAttribute('aria-controls', nav.id);
  navToggle.setAttribute('aria-expanded', 'false');
  navToggle.setAttribute('aria-label', 'Open navigation');
  navToggle.innerHTML = '<span></span><span></span><span></span>';
  navWrap.insertBefore(navToggle, nav);

  const servicesDropdown = nav.querySelector('.services-dropdown');
  let servicesToggle;

  if (servicesDropdown) {
    const servicesLink = servicesDropdown.querySelector('.services-toggle');
    const servicesMenu = servicesDropdown.querySelector('.services-menu');

    if (servicesLink && servicesMenu) {
      servicesLink.classList.replace('services-toggle', 'services-link');
      servicesLink.removeAttribute('aria-haspopup');
      servicesLink.removeAttribute('aria-expanded');
      servicesMenu.id = 'services-menu';
      servicesMenu.removeAttribute('role');
      servicesMenu.querySelectorAll('[role="menuitem"]').forEach((item) => item.removeAttribute('role'));

      servicesToggle = document.createElement('button');
      servicesToggle.className = 'services-toggle';
      servicesToggle.type = 'button';
      servicesToggle.setAttribute('aria-controls', servicesMenu.id);
      servicesToggle.setAttribute('aria-expanded', 'false');
      servicesToggle.setAttribute('aria-label', 'Show service links');
      servicesToggle.innerHTML = 'Services <span class="dropdown-arrow" aria-hidden="true">▾</span>';
      servicesLink.insertAdjacentElement('afterend', servicesToggle);

      servicesToggle.addEventListener('click', () => {
        const isOpen = servicesDropdown.classList.toggle('is-open');
        servicesToggle.setAttribute('aria-expanded', String(isOpen));
        servicesToggle.setAttribute('aria-label', isOpen ? 'Hide service links' : 'Show service links');
      });
    }
  }

  const closeNavigation = () => {
    nav.classList.remove('is-open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Open navigation');
  };

  navToggle.addEventListener('click', () => {
    const isOpen = nav.classList.toggle('is-open');
    navToggle.setAttribute('aria-expanded', String(isOpen));
    navToggle.setAttribute('aria-label', isOpen ? 'Close navigation' : 'Open navigation');
  });

  nav.addEventListener('click', (event) => {
    if (event.target.closest('a')) {
      closeNavigation();
    }
  });

  document.addEventListener('click', (event) => {
    if (!navWrap.contains(event.target)) {
      closeNavigation();
      if (servicesDropdown && servicesToggle) {
        servicesDropdown.classList.remove('is-open');
        servicesToggle.setAttribute('aria-expanded', 'false');
        servicesToggle.setAttribute('aria-label', 'Show service links');
      }
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      closeNavigation();
      if (servicesDropdown && servicesToggle) {
        servicesDropdown.classList.remove('is-open');
        servicesToggle.setAttribute('aria-expanded', 'false');
        servicesToggle.setAttribute('aria-label', 'Show service links');
        servicesToggle.focus();
      }
    }
  });
}

const inquiryForm = document.querySelector('[data-inquiry-form]');

const footer = document.querySelector('footer');
if (footer) {
  const footerLinks = document.createElement('nav');
  footerLinks.className = 'footer-links';
  footerLinks.setAttribute('aria-label', 'Policies and pricing');

  [
    ['Products & Pricing', 'pricing.html'],
    ['Terms of Service', 'terms-of-service.html'],
    ['Privacy Policy', 'privacy-policy.html'],
    ['Refund / Cancellation', 'refund-cancellation.html'],
  ].forEach(([label, path]) => {
    const link = document.createElement('a');
    link.href = `${sitePrefix}${path}`;
    link.textContent = label;
    footerLinks.appendChild(link);
  });

  footer.appendChild(footerLinks);
}

if (inquiryForm) {
  const feedback = inquiryForm.querySelector('[data-form-feedback]');
  const directEmailLinks = document.querySelectorAll('[data-mailto-fallback]');

  inquiryForm.addEventListener('submit', (event) => {
    event.preventDefault();

    if (!inquiryForm.reportValidity()) {
      if (feedback) {
        feedback.textContent = 'Please complete all required fields before sending your inquiry.';
      }
      return;
    }

    const data = new FormData(inquiryForm);
    const name = String(data.get('name') || 'Anonymous');
    const service = String(data.get('service') || 'Not provided');
    const subject = `QuickServ Digital inquiry from ${name}`;
    const body = [
      `Name: ${name}`,
      `Email: ${data.get('email')}`,
      `Business: ${data.get('business') || 'Not provided'}`,
      `Interested in: ${service}`,
      '',
      'Message:',
      data.get('message'),
    ].join('\n');

    const mailtoUrl = `mailto:contact@quickservdigital.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;

    directEmailLinks.forEach((link) => {
      link.href = mailtoUrl;
    });

    qsTrackEvent('lead_form_submit', {
      form_name: 'inquiry_form',
      service,
    });

    if (feedback) {
      feedback.textContent = 'Your message is ready to send. If your email app does not open, use the direct email option below.';
    }

    window.location.href = mailtoUrl;
  });
}

attachAnalyticsHooks();
