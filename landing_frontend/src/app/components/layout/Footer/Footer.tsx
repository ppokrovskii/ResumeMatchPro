const Footer = () => {
    return (
      <footer className="container bg-white shadow-md">
        <div className="mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <p className="text-gray-600">&copy; 2024 Your Company. All rights reserved.</p>
            <nav className="space-x-4">
              <a href="/privacy-policy" className="text-gray-800 hover:text-gray-600">Privacy Policy</a>
              <a href="/terms-of-service" className="text-gray-800 hover:text-gray-600">Terms of Service</a>
            </nav>
          </div>
        </div>
      </footer>
    );
  };
  
  export default Footer;
  