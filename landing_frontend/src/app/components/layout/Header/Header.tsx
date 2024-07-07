// components/Header.tsx
"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import Logo from '../../logo/logo';
import Button from '../../buttons/Button';
import styles from './Header.module.css';

const Header: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const links = [
    { href: '#home', text: 'For HR' },
    { href: '#about', text: 'For Job Seekers' },
    { href: '#services', text: 'How It Works' },
    { href: '#contact', text: 'Contact' },
  ];


  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <header className="w-full bg-bg-secondary absolute z-10">
      <nav className="container mx-auto p-4 flex flex-col text-text-primary">
        <div className="flex justify-between items-center gap-0 md:gap-4 lg:gap-0">
          <div className='flex py-2 md:grow lg:grow-0 text-3xl'>
            <Logo />
          </div>
          <ul className={`hidden lg:flex lg:justify-between gap-4 items-center ${isOpen ? 'grid' : 'hidden'}`}>
            {links.map((link, index) => (
              <li key={index} className='flex items-center'>
                <Link href={link.href} className="block px-2">
                  {link.text}
                </Link>
              </li>
            ))}
            <li className='flex items-center py-2 lg:hidden'>
              <Button variant="primary">Get Early Access</Button>
            </li>
          </ul>
          <div className="hidden md:flex lg:py-2">
            <Button variant="primary">Get Early Access</Button>
          </div>
          <div className="lg:hidden lg:items-center lg:py-2">
            <button
              className="flex items-center lg:hidden focus:outline-none"
              onClick={toggleMenu}
              aria-label="Toggle menu"
            >
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
        <div className={`${isOpen ? 'flex' : 'hidden'} lg:hidden items-center`}>
          {/* <div className='grow'>
             
        </div> */}
          <ul className={`items-start ${styles.fadeInMoveRight} ${isOpen ? 'flex flex-col' : 'hidden'}`}>
            {links.map((link, index) => (
              <li key={index} className='flex items-center py-2'>
                <Link href={link.href} className="block px-2">
                  {link.text}
                </Link>
              </li>
            ))}
            <li className='flex items-center py-2 lg:hidden'>
              <Button variant="primary">Get Early Access</Button>
            </li>
          </ul>
          <div className="hidden lg:flex lg:items-center lg:py-2">
            <Button variant="primary">Get Early Access</Button>
          </div>
        </div>
      </nav>
    </header>
  );
};

export default Header;
