// components/Header.tsx
"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';

const Header: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);

    const toggleMenu = () => {
        setIsOpen(!isOpen);
    };

    return (
        <nav className="container text-foreground p-4 shadow-md">
            <div className="mx-auto flex justify-between items-center">
                <h1 className="text-xl font-bold">My Website</h1>
                <button
                    className="md:hidden focus:outline-none"
                    onClick={toggleMenu}
                    aria-label="Toggle menu"
                >
                    {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
                <ul className={`flex flex-row md:space-x-4 ${isOpen ? 'block' : 'hidden'} md:block`}>
                    <li>
                        <Link href="/" className="block py-2 px-4 hover:text-primary">
                            Home
                        </Link>
                    </li>
                    <li>
                        <Link href="/for-hr" className="block py-2 px-4 hover:text-primary">
                            For HR
                        </Link>
                    </li>
                    <li>
                        <Link href="/for-job-seekers" className="block py-2 px-4 hover:text-primary">
                            For Job Seekers
                        </Link>
                    </li>
                    <li>
                        <Link href="/how-it-works" className="block py-2 px-4 hover:text-primary">
                            How it works
                        </Link>
                    </li>
                    <li>
                        <Link href="/contact" className="block py-2 px-4 hover:text-primary">
                            Contact
                        </Link>
                    </li>
                </ul>
            </div>
        </nav>
    );
};

export default Header;
