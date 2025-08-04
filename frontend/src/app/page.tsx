import Link from "next/link";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white">
      <div className="flex flex-col items-center p-8 md:p-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-800 mb-4">
            Medical Note Generator
          </h1>
          <p className="text-gray-600 text-lg max-w-2xl">
            Generate and manage medical notes efficiently with our AI-powered
            platform
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 w-full max-w-4xl">
          <Link
            href="/generate"
            className="group p-8 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:-translate-y-1"
          >
            <div className="flex flex-col h-full">
              <h2 className="text-2xl font-semibold text-gray-800 mb-3 group-hover:text-blue-600">
                Generate New Note
              </h2>
              <p className="text-gray-600 flex-grow">
                Create a new medical note by entering your observations. Our AI
                will help format and structure your notes.
              </p>
              <div className="mt-4 text-blue-600 group-hover:text-blue-700 font-medium">
                Get Started →
              </div>
            </div>
          </Link>

          <Link
            href="/saved-notes"
            className="group p-8 bg-white border border-gray-200 rounded-xl shadow-sm hover:shadow-md transition-all duration-200 transform hover:-translate-y-1"
          >
            <div className="flex flex-col h-full">
              <h2 className="text-2xl font-semibold text-gray-800 mb-3 group-hover:text-blue-600">
                View Saved Notes
              </h2>
              <p className="text-gray-600 flex-grow">
                Access your archive of generated notes. Review, edit, and manage
                your previous medical documentation.
              </p>
              <div className="mt-4 text-blue-600 group-hover:text-blue-700 font-medium">
                View Notes →
              </div>
            </div>
          </Link>
        </div>

        <footer className="mt-16 text-center text-gray-500">
          <p className="text-sm">
            Select an option above to begin working with your medical notes
          </p>
        </footer>
      </div>
    </div>
  );
}
