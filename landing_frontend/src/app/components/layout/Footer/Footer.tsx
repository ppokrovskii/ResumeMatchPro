import Logo from "../../logo/logo";


const Footer = () => {
  return (
    <footer className="w-full bg-bg-secondary">
      <div className="container mx-auto p-4 sm:px-6 lg:px-8 flex justify-center sm:justify-between items-center">
        <div className='hidden sm:flex py-2 text-xl'>
          <Logo />
        </div>
        <nav className="space-x-4">
          <a href="/privacy-policy" className="text-text-secondary hover:text-gray-600">Privacy Policy</a>
          <a href="/terms-of-service" className="text-text-secondary hover:text-gray-600">Terms of Service</a>
        </nav>
      </div>
    </footer>
  );
};

export default Footer;
