#include <iostream> // Includes the IO stream Library
#include <string>

int main()
{
    std::string userInput; //Declaring user input variable

    std::cout << "Hello World"; // Outputs Hello World to the console
    std::cout << "Press A key to close this window." << std::endl; // Outputs to console

        std::cin >> userInput; //Gets user input
       
       //conditional logic based on input
        if (userInput ==  "a" || userInput == "A") { // Case-insensitive comparison
            std::cout << "Good reading comprehension! Exiting program..." << std::endl;
            return 0; //Exiting program early
        }
        else {
            std::cout << "Can you read?" << userInput << std::endl;
        }


        return 0;// Returns 0 to the OS
}