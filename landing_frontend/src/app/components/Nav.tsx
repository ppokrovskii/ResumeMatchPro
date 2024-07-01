// components/Nav.tsx
"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import Logo from './logo/logo';

const Nav: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    
    <nav className="w-full bg-bg p-4 shadow-md flex justify-between items-start lg:items-center">
      <div className='flex flex-grow py-2 px-4'>
        <Logo />
      </div>
      <ul className={`lg:flex lg:flex-row py-2 ${isOpen ? 'grid' : 'hidden'}`}>
          <li className='flex items-center py-2'>
            <Link href="/" className="block px-4 hover:text-primary">
              Home
            </Link>
          </li>
          <li className='flex items-center py-2'>
            <Link href="/for-hr" className="block px-4 hover:text-primary">
              For HR
            </Link>
          </li>
          <li className='flex items-center py-2'>
            <Link href="/for-job-seekers" className="block px-4 hover:text-primary">
              For Job Seekers
            </Link>
          </li>
          <li className='flex items-center py-2'>
            <Link href="/how-it-works" className="block px-4 hover:text-primary">
              How it works
            </Link>
          </li>
          <li className='flex items-center py-2'>
            <Link href="/contact" className="block px-4 hover:text-primary">
              Contact
            </Link>
          </li>
        </ul>
      <button
          className="lg:hidden focus:outline-none py-2 px-4"
          onClick={toggleMenu}
          aria-label="Toggle menu"
        >
          {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
    </nav>
  );
};

export default Nav;
