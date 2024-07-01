import Button from "../../buttons/Button";

const Content = () => {
    return (
        <main className="grow bg-gray-100">
            <div className="mx-auto px-4 py-8 sm:px-6 lg:px-8">
                <h1 className="text-2xl font-semibold text-gray-800 mb-4">Main Content</h1>
                <p className="text-gray-700">
                    This is the main content area. You can add more components, sections, or text here as needed.
                </p>
                <Button variant="primary">Primary Button</Button>
                <Button variant="secondary">Secondary Button</Button>
            </div>
        </main>
    );
};

export default Content;
