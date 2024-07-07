import Button from "../../buttons/Button";

const Main = () => {
    return (
        <main className="container pt-32">
            <div className="mx-auto p-8">
                <h1 className="text-2xl font-semibold mb-4">Main Content</h1>
                <p className="">
                    This is the main content area. You can add more components, sections, or text here as needed.
                </p>
            </div>
            <div className="flex justify-center p-8">
                <div className="flex flex-col gap-2">
                    <Button className="grow">Regular Button</Button>
                    <Button className="grow" variant="primary">Primary Button</Button>
                    <Button className="grow" variant="secondary">Secondary Button</Button>
                    <Button className="grow" variant="accent">Accent Button</Button>
                </div>
            </div>
        </main>
    );
};

export default Main;
