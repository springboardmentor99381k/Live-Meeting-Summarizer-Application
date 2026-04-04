import React from "react";

function Status({ status }) {
  return (
    <div className="mt-6 text-center">
      <h3 className="text-lg font-semibold">
        Status: <span className="capitalize text-blue-600">{status}</span>
      </h3>

      {status !== "completed" && (
        <div className="flex justify-center mt-4">
          <div className="w-8 h-8 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
        </div>
      )}
    </div>
  );
}

export default Status;