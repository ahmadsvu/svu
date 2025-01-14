from flask import Flask, render_template, request, jsonify
import random
app = Flask(__name__)

# تعريف معلمات الخوارزمية الجينية
POPULATION_SIZE = 10  # حجم السكان
GENERATIONS = 100     # عدد الأجيال
MUTATION_RATE = 0.1   # معدل الطفرة

# وظائف الخوارزمية الجينية
def create_individual(customers, num_windows):
    """إنشاء فرد عشوائي (حل عشوائي)"""
    return [random.randint(0, num_windows - 1) for _ in range(len(customers))]

def calculate_fitness(individual, customers, num_windows):
    """حساب اللياقة للحل (الوقت الإجمالي لأطول شباك)"""
    windows = [0] * num_windows
    for i, window in enumerate(individual):
        windows[window] += customers[i]["duration"]
    return max(windows)  # نريد تقليل أطول وقت انتظار

def crossover(parent1, parent2):
    """تقاطع بين والدين لإنتاج طفل"""
    point = random.randint(1, len(parent1) - 1)
    child = parent1[:point] + parent2[point:]
    return child

def mutate(individual, mutation_rate, num_windows):
    """تطبيق الطفرة على الفرد"""
    for i in range(len(individual)):
        if random.random() < mutation_rate:
            individual[i] = random.randint(0, num_windows - 1)
    return individual

def genetic_algorithm(customers, num_windows, population_size, generations, mutation_rate):
    """الخوارزمية الجينية الرئيسية"""
    population = [create_individual(customers, num_windows) for _ in range(population_size)]

    for generation in range(generations):
        fitness_scores = [calculate_fitness(ind, customers, num_windows) for ind in population]
        sorted_population = [x for _, x in sorted(zip(fitness_scores, population), key=lambda pair: pair[0])]
        next_generation = sorted_population[:population_size // 2]

        while len(next_generation) < population_size:
            parent1, parent2 = random.sample(next_generation, 2)
            child = crossover(parent1, parent2)
            child = mutate(child, mutation_rate, num_windows)
            next_generation.append(child)

        population = next_generation

    best_individual = min(population, key=lambda ind: calculate_fitness(ind, customers, num_windows))
    return best_individual, calculate_fitness(best_individual, customers, num_windows)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # جمع البيانات من النموذج
            num_windows = int(request.form["num_windows"])
            num_customers = int(request.form["num_customers"])
            customers = []

            for i in range(1, num_customers + 1):
                customer_id = int(request.form.get(f"customer{i}_id", 0))
                duration = int(request.form.get(f"customer{i}_duration", 0))
                customers.append({"id": customer_id, "duration": duration})

            # تشغيل الخوارزمية
            best_solution, best_fitness = genetic_algorithm(customers, num_windows, POPULATION_SIZE, GENERATIONS, MUTATION_RATE)

            # تحضير النتائج للعرض
            windows = [[] for _ in range(num_windows)]
            for i, window in enumerate(best_solution):
                windows[window].append(customers[i]["id"])

            results = {
                "best_solution": best_solution,
                "best_fitness": best_fitness,
                "windows": windows
            }

            return render_template("index.html", results=results)

        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)