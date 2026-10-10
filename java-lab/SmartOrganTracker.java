import java.util.Scanner;

public class SmartOrganTracker {

    static Scanner sc = new Scanner(System.in);

    // ============================================================
    // CUSTOM EXCEPTIONS
    // ============================================================

    static class InvalidInputException extends Exception {
        InvalidInputException(String message) {
            super(message);
        }
    }

    static class OrganNotFoundException extends Exception {
        OrganNotFoundException(String message) {
            super(message);
        }
    }

    static class RecipientNotFoundException extends Exception {
        RecipientNotFoundException(String message) {
            super(message);
        }
    }

    // ============================================================
    // ORGAN CLASS
    // ============================================================

    static class Organ {
        String organId;
        String organType;
        String bloodGroup;
        int maxViabilityHours;

        double elapsedHours;
        String status;

        Organ(String organId, String organType,
              String bloodGroup, int maxViabilityHours) {

            this.organId = organId;
            this.organType = organType;
            this.bloodGroup = bloodGroup;
            this.maxViabilityHours = maxViabilityHours;

            this.elapsedHours = 0;
            this.status = "REGISTERED";
        }

        double getRemainingViability() {
            return maxViabilityHours - elapsedHours;
        }

        void updateViability(double hours) throws InvalidInputException {

            if (hours < 0) {
                throw new InvalidInputException(
                        "Elapsed time cannot be negative."
                );
            }

            if (hours > maxViabilityHours) {
                elapsedHours = maxViabilityHours;
            } else {
                elapsedHours = hours;
            }

            updateStatus();
        }

        void updateStatus() {

            double remaining = getRemainingViability();

            if (remaining <= 0) {
                status = "CRITICAL";
            }
            else if (remaining <= 2) {
                status = "WARNING";
            }
            else {
                status = "SAFE";
            }
        }

        void display() {

            System.out.println("--------------------------------");
            System.out.println("Organ ID          : " + organId);
            System.out.println("Organ Type        : " + organType);
            System.out.println("Blood Group       : " + bloodGroup);
            System.out.println("Maximum Viability : " + maxViabilityHours + " hours");
            System.out.println("Elapsed Time      : " + elapsedHours + " hours");
            System.out.println("Remaining Time    : "
                    + getRemainingViability() + " hours");
            System.out.println("Status            : " + status);
            System.out.println("--------------------------------");
        }
    }

    // ============================================================
    // RECIPIENT CLASS
    // ============================================================

    static class Recipient {

        String recipientId;
        String organType;
        String bloodGroup;

        int urgency;
        int waitingDays;

        Recipient(String recipientId,
                  String organType,
                  String bloodGroup,
                  int urgency,
                  int waitingDays) {

            this.recipientId = recipientId;
            this.organType = organType;
            this.bloodGroup = bloodGroup;
            this.urgency = urgency;
            this.waitingDays = waitingDays;
        }

        void display() {

            System.out.println(
                    recipientId + " | "
                    + organType + " | "
                    + bloodGroup + " | Urgency: "
                    + urgency + " | Waiting: "
                    + waitingDays + " days"
            );
        }
    }

    // ============================================================
    // CHECKPOINT CLASS
    // ============================================================

    static class Checkpoint {

        String location;
        String time;
        double temperature;
        String status;

        Checkpoint(String location,
                   String time,
                   double temperature) {

            this.location = location;
            this.time = time;
            this.temperature = temperature;

            if (temperature >= 2 && temperature <= 8) {
                status = "SAFE";
            }
            else {
                status = "COLD-CHAIN ALERT";
            }
        }

        void display() {

            System.out.println(
                    location + " | "
                    + time + " | "
                    + temperature + " C | "
                    + status
            );
        }
    }

    // ============================================================
    // ORGAN JOURNEY - LINKED LIST
    // ============================================================

    static class JourneyNode {

        Checkpoint checkpoint;
        JourneyNode next;

        JourneyNode(Checkpoint checkpoint) {
            this.checkpoint = checkpoint;
            this.next = null;
        }
    }

    static class OrganJourney {

        JourneyNode head;
        JourneyNode tail;

        void addCheckpoint(Checkpoint checkpoint) {

            JourneyNode newNode =
                    new JourneyNode(checkpoint);

            if (head == null) {
                head = newNode;
                tail = newNode;
            }
            else {
                tail.next = newNode;
                tail = newNode;
            }
        }

        void displayJourney() {

            if (head == null) {
                System.out.println("No journey checkpoints available.");
                return;
            }

            System.out.println("\n===== ORGAN JOURNEY =====");

            JourneyNode current = head;

            while (current != null) {

                current.checkpoint.display();

                current = current.next;
            }
        }
    }

    // ============================================================
    // QUEUE - ARRAY IMPLEMENTATION
    // ============================================================

    static class CheckpointQueue {

        Checkpoint[] queue;
        int front;
        int rear;
        int size;

        CheckpointQueue(int capacity) {

            queue = new Checkpoint[capacity];

            front = 0;
            rear = -1;
            size = 0;
        }

        boolean isEmpty() {
            return size == 0;
        }

        boolean isFull() {
            return size == queue.length;
        }

        void enqueue(Checkpoint checkpoint)
                throws InvalidInputException {

            if (isFull()) {
                throw new InvalidInputException(
                        "Checkpoint queue is full."
                );
            }

            rear = (rear + 1) % queue.length;

            queue[rear] = checkpoint;

            size++;
        }

        Checkpoint dequeue()
                throws InvalidInputException {

            if (isEmpty()) {
                throw new InvalidInputException(
                        "No checkpoints available."
                );
            }

            Checkpoint checkpoint = queue[front];

            queue[front] = null;

            front = (front + 1) % queue.length;

            size--;

            return checkpoint;
        }

        void display() {

            if (isEmpty()) {
                System.out.println("Queue is empty.");
                return;
            }

            System.out.println("\n===== TRANSIT QUEUE =====");

            int index = front;

            for (int i = 0; i < size; i++) {

                queue[index].display();

                index = (index + 1) % queue.length;
            }
        }
    }

    // ============================================================
    // STACK - ARRAY IMPLEMENTATION
    // ============================================================

    static class AuditStack {

        String[] stack;
        int top;

        AuditStack(int capacity) {

            stack = new String[capacity];

            top = -1;
        }

        boolean isEmpty() {
            return top == -1;
        }

        boolean isFull() {
            return top == stack.length - 1;
        }

        void push(String action)
                throws InvalidInputException {

            if (isFull()) {
                throw new InvalidInputException(
                        "Audit stack is full."
                );
            }

            stack[++top] = action;
        }

        String pop()
                throws InvalidInputException {

            if (isEmpty()) {
                throw new InvalidInputException(
                        "No audit actions available."
                );
            }

            return stack[top--];
        }

        void display() {

            if (isEmpty()) {
                System.out.println("No audit actions.");
                return;
            }

            System.out.println("\n===== RECENT ACTIONS =====");

            for (int i = top; i >= 0; i--) {

                System.out.println(stack[i]);
            }
        }
    }

    // ============================================================
    // MAIN DATA ARRAYS
    // ============================================================

    static Organ[] organs = new Organ[20];

    static Recipient[] recipients = new Recipient[50];

    static int organCount = 0;
    static int recipientCount = 0;

    static CheckpointQueue transitQueue =
            new CheckpointQueue(50);

    static AuditStack auditLog =
            new AuditStack(100);

    static OrganJourney journey =
            new OrganJourney();


    // ============================================================
    // INPUT VALIDATION METHODS
    // ============================================================

    static String readNonEmpty(String message)
            throws InvalidInputException {

        System.out.print(message);

        String input = sc.nextLine().trim();

        if (input.length() == 0) {

            throw new InvalidInputException(
                    "Input cannot be empty."
            );
        }

        return input;
    }

    static int readPositiveInt(String message)
            throws InvalidInputException {

        System.out.print(message);

        String input = sc.nextLine();

        try {

            int value = Integer.parseInt(input);

            if (value <= 0) {

                throw new InvalidInputException(
                        "Value must be greater than zero."
                );
            }

            return value;

        } catch (NumberFormatException e) {

            throw new InvalidInputException(
                    "Please enter a valid integer."
            );
        }
    }

    static double readPositiveDouble(String message)
            throws InvalidInputException {

        System.out.print(message);

        String input = sc.nextLine();

        try {

            double value = Double.parseDouble(input);

            if (value < 0) {

                throw new InvalidInputException(
                        "Value cannot be negative."
                );
            }

            return value;

        } catch (NumberFormatException e) {

            throw new InvalidInputException(
                    "Please enter a valid number."
            );
        }
    }


    // ============================================================
    // FIND ORGAN - LINEAR SEARCH
    // ============================================================

    static int findOrgan(String organId) {

        for (int i = 0; i < organCount; i++) {

            if (organs[i].organId.equalsIgnoreCase(organId)) {

                return i;
            }
        }

        return -1;
    }


    // ============================================================
    // FIND RECIPIENT - LINEAR SEARCH
    // ============================================================

    static int findRecipient(String recipientId) {

        for (int i = 0; i < recipientCount; i++) {

            if (recipients[i].recipientId
                    .equalsIgnoreCase(recipientId)) {

                return i;
            }
        }

        return -1;
    }


    // ============================================================
    // ORGAN REGISTRATION
    // ============================================================

    static void registerOrgan() {

        try {

            if (organCount == organs.length) {

                throw new InvalidInputException(
                        "Maximum organ storage reached."
                );
            }

            String id =
                    readNonEmpty("Enter Organ ID: ");

            if (findOrgan(id) != -1) {

                throw new InvalidInputException(
                        "Organ ID already exists."
                );
            }

            String type =
                    readNonEmpty("Enter Organ Type: ");

            String blood =
                    readNonEmpty("Enter Blood Group: ");

            int viability =
                    readPositiveInt(
                            "Enter Maximum Viability (hours): "
                    );

            organs[organCount] =
                    new Organ(
                            id,
                            type,
                            blood,
                            viability
                    );

            organCount++;

            auditLog.push(
                    "Organ Registered: " + id
            );

            System.out.println(
                    "\nOrgan registered successfully."
            );

        }
        catch (InvalidInputException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
    }


    // ============================================================
    // ADD RECIPIENT
    // ============================================================

    static void addRecipient() {

        try {

            if (recipientCount == recipients.length) {

                throw new InvalidInputException(
                        "Maximum recipient storage reached."
                );
            }

            String id =
                    readNonEmpty("Enter Recipient ID: ");

            if (findRecipient(id) != -1) {

                throw new InvalidInputException(
                        "Recipient ID already exists."
                );
            }

            String type =
                    readNonEmpty("Required Organ Type: ");

            String blood =
                    readNonEmpty("Blood Group: ");

            int urgency =
                    readPositiveInt(
                            "Urgency (1-3): "
                    );

            if (urgency > 3) {

                throw new InvalidInputException(
                        "Urgency must be between 1 and 3."
                );
            }

            int waiting =
                    readPositiveInt(
                            "Waiting Days: "
                    );

            recipients[recipientCount] =
                    new Recipient(
                            id,
                            type,
                            blood,
                            urgency,
                            waiting
                    );

            recipientCount++;

            auditLog.push(
                    "Recipient Added: " + id
            );

            System.out.println(
                    "\nRecipient added successfully."
            );

        }
        catch (InvalidInputException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
    }


    // ============================================================
    // BLOOD GROUP COMPATIBILITY
    // ============================================================

    static boolean bloodCompatible(
            String organBlood,
            String recipientBlood) {

        /*
         * Simplified compatibility rules
         * for project simulation.
         */

        if (organBlood.equalsIgnoreCase("O-")) {

            return true;
        }

        if (organBlood.equalsIgnoreCase("O+")) {

            return recipientBlood.equalsIgnoreCase("O+")
                    || recipientBlood.equalsIgnoreCase("AB+");
        }

        if (organBlood.equalsIgnoreCase("A+")) {

            return recipientBlood.equalsIgnoreCase("A+")
                    || recipientBlood.equalsIgnoreCase("AB+");
        }

        if (organBlood.equalsIgnoreCase("B+")) {

            return recipientBlood.equalsIgnoreCase("B+")
                    || recipientBlood.equalsIgnoreCase("AB+");
        }

        if (organBlood.equalsIgnoreCase("AB+")) {

            return recipientBlood.equalsIgnoreCase("AB+");
        }

        return organBlood.equalsIgnoreCase(recipientBlood);
    }


    // ============================================================
    // RECIPIENT MATCHING
    // LINEAR SEARCH + ARRAY
    // ============================================================

    static void findCompatibleRecipients() {

        try {

            String organId =
                    readNonEmpty("Enter Organ ID: ");

            int index = findOrgan(organId);

            if (index == -1) {

                throw new OrganNotFoundException(
                        "Organ not found."
                );
            }

            Organ organ = organs[index];

            Recipient[] eligible =
                    new Recipient[recipientCount];

            int eligibleCount = 0;

            for (int i = 0;
                 i < recipientCount;
                 i++) {

                Recipient r = recipients[i];

                boolean organMatch =
                        organ.organType.equalsIgnoreCase(
                                r.organType
                        );

                boolean bloodMatch =
                        bloodCompatible(
                                organ.bloodGroup,
                                r.bloodGroup
                        );

                if (organMatch && bloodMatch) {

                    eligible[eligibleCount++] = r;
                }
            }

            if (eligibleCount == 0) {

                System.out.println(
                        "\nNo compatible recipients found."
                );

                return;
            }

            // ====================================================
            // SORTING
            // Higher urgency first.
            // If urgency is same, longer waiting first.
            // ====================================================

            for (int i = 0;
                 i < eligibleCount - 1;
                 i++) {

                for (int j = 0;
                     j < eligibleCount - i - 1;
                     j++) {

                    boolean swap = false;

                    if (eligible[j].urgency
                            < eligible[j + 1].urgency) {

                        swap = true;
                    }

                    else if (
                            eligible[j].urgency
                            == eligible[j + 1].urgency
                            &&
                            eligible[j].waitingDays
                            < eligible[j + 1].waitingDays) {

                        swap = true;
                    }

                    if (swap) {

                        Recipient temp =
                                eligible[j];

                        eligible[j] =
                                eligible[j + 1];

                        eligible[j + 1] =
                                temp;
                    }
                }
            }

            System.out.println(
                    "\n===== ELIGIBLE RECIPIENTS ====="
            );

            for (int i = 0;
                 i < eligibleCount;
                 i++) {

                System.out.print(
                        (i + 1) + ". "
                );

                eligible[i].display();
            }

            auditLog.push(
                    "Compatibility Checked: " + organId
            );

        }
        catch (OrganNotFoundException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
        catch (InvalidInputException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
    }


    // ============================================================
    // START TRANSIT
    // ============================================================

    static void startTransit() {

        try {

            String organId =
                    readNonEmpty("Enter Organ ID: ");

            int index = findOrgan(organId);

            if (index == -1) {

                throw new OrganNotFoundException(
                        "Organ not found."
                );
            }

            Organ organ = organs[index];

            if (organ.status.equals("CRITICAL")) {

                System.out.println(
                        "WARNING: Organ is already CRITICAL."
                );
            }

            organ.status = "IN TRANSIT";

            auditLog.push(
                    "Transit Started: " + organId
            );

            System.out.println(
                    "Transit started successfully."
            );

        }
        catch (OrganNotFoundException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
        catch (InvalidInputException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
    }


    // ============================================================
    // ADD CHECKPOINT
    // ============================================================

    static void addCheckpoint() {

        try {

            String location =
                    readNonEmpty("Enter Location: ");

            String time =
                    readNonEmpty("Enter Time: ");

            double temperature =
                    readPositiveDouble(
                            "Enter Temperature (C): "
                    );

            Checkpoint checkpoint =
                    new Checkpoint(
                            location,
                            time,
                            temperature
                    );

            transitQueue.enqueue(checkpoint);

            journey.addCheckpoint(checkpoint);

            auditLog.push(
                    "Checkpoint Updated: "
                            + location
            );

            System.out.println(
                    "\nCheckpoint added."
            );

            if (checkpoint.status
                    .equals("COLD-CHAIN ALERT")) {

                System.out.println(
                        "WARNING: COLD-CHAIN ALERT!"
                );

                auditLog.push(
                        "Cold-chain Warning: "
                                + location
                );
            }

        }
        catch (InvalidInputException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
    }


    // ============================================================
    // UPDATE VIABILITY
    // ============================================================

    static void updateViability() {

        try {

            String organId =
                    readNonEmpty("Enter Organ ID: ");

            int index =
                    findOrgan(organId);

            if (index == -1) {

                throw new OrganNotFoundException(
                        "Organ not found."
                );
            }

            double elapsed =
                    readPositiveDouble(
                            "Enter total elapsed transit time (hours): "
                    );

            organs[index].updateViability(
                    elapsed
            );

            System.out.println(
                    "\nViability Updated."
            );

            organs[index].display();

            if (organs[index].status
                    .equals("WARNING")) {

                System.out.println(
                        "WARNING: Remaining viability is low."
                );
            }

            if (organs[index].status
                    .equals("CRITICAL")) {

                System.out.println(
                        "CRITICAL: Immediate action required."
                );

                auditLog.push(
                        "Emergency Activated: "
                                + organId
                );
            }

        }
        catch (OrganNotFoundException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
        catch (InvalidInputException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
    }


    // ============================================================
    // EMERGENCY TRANSIT
    // ============================================================

    static void emergencyHandling() {

        try {

            String organId =
                    readNonEmpty("Enter Organ ID: ");

            int index =
                    findOrgan(organId);

            if (index == -1) {

                throw new OrganNotFoundException(
                        "Organ not found."
                );
            }

            Organ organ = organs[index];

            double remaining =
                    organ.getRemainingViability();

            if (remaining <= 2) {

                organ.status =
                        "EMERGENCY TRANSIT";

                auditLog.push(
                        "Emergency Activated: "
                                + organId
                );

                System.out.println(
                        "\n🚨 EMERGENCY TRANSIT ACTIVATED"
                );

                System.out.println(
                        "Organ: " + organId
                );

                System.out.println(
                        "Remaining viability: "
                                + remaining
                                + " hours"
                );

            }
            else {

                System.out.println(
                        "Emergency not required."
                );

                System.out.println(
                        "Remaining viability: "
                                + remaining
                                + " hours"
                );
            }

        }
        catch (OrganNotFoundException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
        catch (InvalidInputException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
    }


    // ============================================================
    // INTERRUPTED TRANSIT
    // ============================================================

    static void interruptTransit() {

        try {

            String organId =
                    readNonEmpty("Enter Organ ID: ");

            int index =
                    findOrgan(organId);

            if (index == -1) {

                throw new OrganNotFoundException(
                        "Organ not found."
                );
            }

            Organ organ = organs[index];

            organ.status =
                    "TRANSPORT INTERRUPTED";

            auditLog.push(
                    "Transit Interrupted: "
                            + organId
            );

            System.out.println(
                    "\nTRANSPORT INTERRUPTED"
            );

            System.out.println(
                    "Remaining viability: "
                            + organ.getRemainingViability()
                            + " hours"
            );

            if (organ.getRemainingViability()
                    <= 2) {

                organ.status =
                        "EMERGENCY TRANSIT";

                auditLog.push(
                        "Emergency Activated after interruption: "
                                + organId
                );

                System.out.println(
                        "🚨 Organ placed in urgent handling."
                );
            }

        }
        catch (OrganNotFoundException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
        catch (InvalidInputException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
    }


    // ============================================================
    // DELIVERY
    // ============================================================

    static void completeDelivery() {

        try {

            String organId =
                    readNonEmpty("Enter Organ ID: ");

            int index =
                    findOrgan(organId);

            if (index == -1) {

                throw new OrganNotFoundException(
                        "Organ not found."
                );
            }

            Organ organ = organs[index];

            if (organ.getRemainingViability() <= 0) {

                throw new InvalidInputException(
                        "Delivery cannot be completed. "
                                + "Organ viability has expired."
                );
            }

            organ.status =
                    "DELIVERED";

            auditLog.push(
                    "Delivery Completed: "
                            + organId
            );

            System.out.println(
                    "\nDelivery completed successfully."
            );

        }
        catch (OrganNotFoundException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
        catch (InvalidInputException e) {

            System.out.println(
                    "ERROR: " + e.getMessage()
            );
        }
    }


    // ============================================================
    // DISPLAY ALL ORGANS
    // ============================================================

    static void displayOrgans() {

        if (organCount == 0) {

            System.out.println(
                    "No organs registered."
            );

            return;
        }

        System.out.println(
                "\n===== REGISTERED ORGANS ====="
        );

        for (int i = 0;
             i < organCount;
             i++) {

            organs[i].display();
        }
    }


    // ============================================================
    // DISPLAY ALL RECIPIENTS
    // ============================================================

    static void displayRecipients() {

        if (recipientCount == 0) {

            System.out.println(
                    "No recipients registered."
            );

            return;
        }

        System.out.println(
                "\n===== RECIPIENTS ====="
        );

        for (int i = 0;
             i < recipientCount;
             i++) {

            recipients[i].display();
        }
    }


    // ============================================================
    // MAIN MENU
    // ============================================================

    static void menu() {

        while (true) {

            System.out.println(
                    "\n========================================"
            );

            System.out.println(
                    " SMART ORGAN MATCH & "
                    + "COLD-CHAIN TRANSIT TRACKER"
            );

            System.out.println(
                    "========================================"
            );

            System.out.println("1. Register Organ");
            System.out.println("2. Add Recipient");
            System.out.println("3. Find Compatible Recipients");
            System.out.println("4. Start Transit");
            System.out.println("5. Add Transit Checkpoint");
            System.out.println("6. Update Organ Viability");
            System.out.println("7. Emergency Transit Handling");
            System.out.println("8. Interrupt Transit");
            System.out.println("9. Complete Delivery");
            System.out.println("10. Display Organ Journey");
            System.out.println("11. Display Transit Queue");
            System.out.println("12. Display Audit Trail");
            System.out.println("13. Display All Organs");
            System.out.println("14. Display All Recipients");
            System.out.println("15. Exit");

            System.out.print(
                    "\nEnter your choice: "
            );

            String input = sc.nextLine();

            int choice;

            try {

                choice =
                        Integer.parseInt(input);

            }
            catch (NumberFormatException e) {

                System.out.println(
                        "ERROR: Please enter a valid menu number."
                );

                continue;
            }

            switch (choice) {

                case 1:
                    registerOrgan();
                    break;

                case 2:
                    addRecipient();
                    break;

                case 3:
                    findCompatibleRecipients();
                    break;

                case 4:
                    startTransit();
                    break;

                case 5:
                    addCheckpoint();
                    break;

                case 6:
                    updateViability();
                    break;

                case 7:
                    emergencyHandling();
                    break;

                case 8:
                    interruptTransit();
                    break;

                case 9:
                    completeDelivery();
                    break;

                case 10:
                    journey.displayJourney();
                    break;

                case 11:
                    transitQueue.display();
                    break;

                case 12:
                    auditLog.display();
                    break;

                case 13:
                    displayOrgans();
                    break;

                case 14:
                    displayRecipients();
                    break;

                case 15:

                    System.out.println(
                            "\nThank you for using "
                                    + "Smart Organ Tracker."
                    );

                    return;

                default:

                    System.out.println(
                            "ERROR: Invalid menu choice."
                    );
            }
        }
    }


    // ============================================================
    // MAIN
    // ============================================================

    public static void main(String[] args) {

        System.out.println(
                "========================================"
        );

        System.out.println(
                "   SMART ORGAN TRACKER"
        );

        System.out.println(
                "   DSA Project"
        );

        System.out.println(
                "========================================"
        );

        menu();
    }
}