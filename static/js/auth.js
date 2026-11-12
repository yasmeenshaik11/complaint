
async function post(url, data) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(data),
      signal: controller.signal
    });

    let result;

    try {
      result = await response.json();
    } catch {
      throw new Error(
        `Server returned an invalid response (${response.status}).`
      );
    }

    if (!response.ok && result.success === undefined) {
      throw new Error(
        result.message || `Request failed (${response.status}).`
      );
    }

    return result;
  } catch (error) {
    if (error.name === "AbortError") {
      throw new Error(
        "Login timed out. Check Flask and the database."
      );
    }

    throw error;
  } finally {
    clearTimeout(timeout);
  }
}

// Citizen and Official Login
const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const message = document.getElementById("msg");
    const button = loginForm.querySelector('button[type="submit"]');

    const data = Object.fromEntries(new FormData(loginForm));
    const isOfficial =
      window.location.pathname.replace(/\/+$/, "") === "/authority/login";

    message.textContent = "Signing in...";

    if (button) {
      button.disabled = true;
    }

    try {
      const result = await post("/api/login", data);

      if (!result.success) {
        message.textContent =
          result.message || "Invalid email or password.";
        return;
      }

      const user = result.data?.user;
      const token = result.data?.access_token;

      if (!user || !token) {
        message.textContent =
          "Login response is incomplete. Please contact the administrator.";
        return;
      }

      if (isOfficial && !["AUTHORITY", "ADMIN"].includes(user.role)) {
        message.textContent =
          "This account is not an official account.";
        return;
      }

      if (!isOfficial && user.role !== "CITIZEN") {
        message.textContent =
          "Please use the Official Login page.";
        return;
      }

      localStorage.setItem("token", token);
      localStorage.setItem("user", JSON.stringify(user));

      message.textContent = "Login successful. Opening dashboard...";

      window.location.assign(isOfficial ? "/authority" : "/citizen");

    } catch (error) {
      console.error("Login error:", error);

      message.textContent =
        error.message || "Unable to connect to the server.";
    } finally {
      if (button) {
        button.disabled = false;
      }
    }
  });
}

// Citizen Registration
const registerForm = document.getElementById("registerForm");

if (registerForm) {
  registerForm.addEventListener("submit", async function (event) {
    event.preventDefault();

    const message = document.getElementById("msg");
    const button = registerForm.querySelector('button[type="submit"]');
    const data = Object.fromEntries(new FormData(registerForm));

    if (data.password !== data.confirm) {
      message.textContent = "Passwords do not match.";
      return;
    }

    delete data.confirm;
    message.textContent = "Creating account...";

    if (button) {
      button.disabled = true;
    }

    try {
      const result = await post("/api/register", data);

      if (result.success) {
        message.textContent =
          "Registration successful. Redirecting to login...";

        setTimeout(() => {
          window.location.assign("/login");
        }, 700);
      } else {
        message.textContent =
          result.message || "Registration failed.";
      }
    } catch (error) {
      console.error("Registration error:", error);

      message.textContent =
        error.message || "Unable to connect to the server.";
    } finally {
      if (button) {
        button.disabled = false;
      }
    }
  });
}
